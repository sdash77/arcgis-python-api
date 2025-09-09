import argparse
import json
from testrail import APIClient
import xmltodict
from timeit import default_timer as timer
import os.path

# from ExtractBuildAndVersion import getEndeavourBuild, getPortalBuild, getServerBuild

#
# This Script is used to report Test Results from JUnit and SoapUI to TestRails
# The Script needs Python 3.6.x minimum and xmltodict package needs to be installed using PIP/Conda etc.
#
# The script is invoked using the following:
#

failedTests = []
passedTests = []


def Setup(username, password):
    client = APIClient("https://esri.testrail.net/")
    client.user = str(username)
    client.password = str(password)
    # client.token = "0FcRTsM3DDMEd6GQipRl-Fmp9hRSTigLhYH2xvVls"
    return client


def process_single_item(
    d, runNumber, version, buildNumber, jenkins, environmentName, matchTestFileName
):
    if "testcase" in d:
        testSuiteName = d["@name"].split(".")[-1]
        print("Test Suite name: " + testSuiteName)
        # create the testcase<->ID map
        testcaseMap = GetTestCaseMap(
            client, runNumber, testSuiteName, matchTestFileName
        )
        existingTests = {}
        for test in d["testcase"]:
            try:
                existingTests[str(test["@name"])] = False
            except Exception as ex:
                # This part is annoying.
                # d['testcase'] -> test should have a dictionary of {'@name':'a','@time':'b'}
                # but when there is only one testcase, test has value '@name'. it does not return a JSON. ANNOYING!!
                print(
                    "Only one Test in XML..... putting hack: "
                    + str(d["testcase"]["@name"])
                )
                existingTests[str(d["testcase"]["@name"])] = False

        for x in range(0, len(d["testcase"])):
            if int(d["@tests"]) > 1:
                temp = d["testcase"][x]
            else:
                temp = d["testcase"]
            class_name = temp["@classname"]
            testCase = temp["@name"]
            stripped_class_name = class_name.split(".")[-1]
            updatedTestCase = f"{testCase}_{stripped_class_name}"
            if updatedTestCase not in testcaseMap:
                print(updatedTestCase + " not reported. test_id not found")
                continue

            if "failure" in temp:
                failedTests.append(testCase)
                if "@message" in temp["failure"]:
                    print(
                        updatedTestCase
                        + "   Failed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["failure"]["@message"])
                    )
                    SetTestStatus(
                        client,
                        testcaseMap[updatedTestCase],
                        5,
                        "Version: "
                        + version
                        + " : "
                        + buildNumber
                        + "        \nFailed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["failure"]["@message"])
                        + str(jenkins)
                        + str(environmentName),
                    )
                else:  # '@type' in temp['failure']:
                    print(
                        updatedTestCase
                        + "   Failed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["failure"]["@type"])
                    )
                    SetTestStatus(
                        client,
                        testcaseMap[updatedTestCase],
                        5,
                        "Version: "
                        + version
                        + " : "
                        + buildNumber
                        + "        \nFailed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["failure"]["@type"])
                        + str(jenkins)
                        + str(environmentName),
                    )
            elif "error" in temp:
                failedTests.append(testCase)
                if "@message" in temp["error"]:
                    print(
                        updatedTestCase
                        + "   Failed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["error"]["@message"])
                    )
                    SetTestStatus(
                        client,
                        testcaseMap[updatedTestCase],
                        5,
                        "Version: "
                        + version
                        + " : "
                        + buildNumber
                        + "        \nFailed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["error"]["@message"])
                        + str(jenkins)
                        + str(environmentName),
                    )
                else:
                    print(
                        updatedTestCase
                        + "   Failed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["error"])
                    )
                    SetTestStatus(
                        client,
                        testcaseMap[updatedTestCase],
                        5,
                        "Version: "
                        + version
                        + " : "
                        + buildNumber
                        + "        \nFailed in :"
                        + str(temp["@time"])
                        + "      Message:"
                        + str(temp["error"])
                        + str(jenkins)
                        + str(environmentName),
                    )

            elif "skipped" in temp:
                print(
                    "No report found for : "
                    + updatedTestCase
                    + " ....Reporting as Skipped"
                )
                SetTestStatus(
                    client,
                    testcaseMap[updatedTestCase],
                    6,
                    "Version: "
                    + version
                    + " : "
                    + buildNumber
                    + "        \nThis test is skipped"
                    + str(environmentName),
                )
            else:
                passedTests.append(testCase)
                print(updatedTestCase + "   Passed in :" + str(temp["@time"]))
                # update status
                SetTestStatus(
                    client,
                    testcaseMap[updatedTestCase],
                    1,
                    "Version: "
                    + version
                    + " : "
                    + buildNumber
                    + "        \nThis test passed in time    "
                    + str(temp["@time"])
                    + str(jenkins)
                    + str(environmentName),
                )
        else:
            print("No test case found in the test suite xml")


def process_array(
    items, runNumber, version, buildNumber, jenkins, environmentName, matchTestFileName
):
    for item in items:
        process_single_item(
            item,
            runNumber,
            version,
            buildNumber,
            jenkins,
            environmentName,
            matchTestFileName,
        )


def convertURL(
    client,
    xml_file,
    xml_attribs,
    runNumber,
    version,
    buildNumber,
    jenkinsURL,
    environmentname,
    matchTestFileName,
):

    jenkins = ""
    if jenkinsURL is not None:
        jenkins = "\nJenkins: " + str(jenkinsURL)

    environmentName = ""
    if environmentname != "":
        environmentName = "\nEnvironment: " + str(environmentname)

    if os.path.isfile(xml_file):
        with open(xml_file, "rb") as f:  # notice the "rb" mode
            parsed_dict = xmltodict.parse(f, xml_attribs=xml_attribs)

            if "testsuites" in parsed_dict:
                d = parsed_dict["testsuites"]
            else:
                d = parsed_dict

            if isinstance(d["testsuite"], list):
                process_array(
                    d["testsuite"],
                    runNumber,
                    version,
                    buildNumber,
                    jenkins,
                    environmentName,
                    matchTestFileName,
                )
            elif isinstance(d["testsuite"], dict):
                process_single_item(
                    d["testsuite"],
                    runNumber,
                    version,
                    buildNumber,
                    jenkins,
                    environmentName,
                    matchTestFileName,
                )
            else:
                print("Invalid data format")

    else:
        # No XML file provided.
        print("User Input XML Test File: " + xml_file + " not found")


def CreateHTMLTableTestResult(build, url, version, suite):
    finalHTML = []

    failCount = len(failedTests)
    passCount = len(passedTests)
    totalCount = failCount + passCount

    # Create Headers
    finalHTML.append("<html>")
    finalHTML.append("<head>")
    finalHTML.append("<style>")
    finalHTML.append("table {")
    finalHTML.append("  font-family: arial, sans-serif;")
    finalHTML.append("  border-collapse: collapse;")
    finalHTML.append("  width: 30%;}")

    finalHTML.append("td, th {")
    finalHTML.append("  border: 1px solid #dddddd;")
    finalHTML.append("  text-align: left;")
    finalHTML.append("  padding: 8px;}")

    finalHTML.append("</style></head><body>")
    finalHTML.append("<br/><pre>")
    finalHTML.append(
        '<font color="red" size="4"><b>Failed:</b> '
        + str(failCount)
        + '</font>		<font color="green" size="4"><b>Pass: </b> '
        + str(passCount)
        + '</font>		<font color="#6699CC" size="4"><b>Total: </b> '
        + str(totalCount)
        + "</font>"
    )
    finalHTML.append("</pre><br/>")
    finalHTML.append("<b>Test Suite: " + suite + "</b><br/>")
    finalHTML.append("<b>Build: " + build + "</b><br/>")
    finalHTML.append("<b>Version: " + version + "</b><br/>")
    finalHTML.append('<b>URL:</b> <a href="' + url + '">Test Report</a><br/>')
    finalHTML.append("<br/><b>Test Summary: </b>")

    finalHTML.append(
        '<table style="font-family: Arial; font-size: 14px; width:30%;" cellpadding="5">'
    )
    for failed in failedTests:
        finalHTML.append(
            '<tr><td><font color="red" size="2">'
            + failed
            + '</font></td><td><font color="red" size="2">FAILED</font></td></tr>'
        )

    for passed in passedTests:
        finalHTML.append(
            '<tr><td><font color="green" size="2">'
            + passed
            + '</font></td><td><font color="green" size="2">PASSED</font></td></tr>'
        )

    finalHTML.append("</table></body></html>")

    with open(
        f"./results/{suite}_test_results.html", "w", encoding="utf-8"
    ) as filehandle:
        for listitem in finalHTML:
            filehandle.write("%s\n" % listitem)


def CreateErrorHTMLResult(jenkinsurl, deploymenturl):
    finalHTML = []

    # Create Headers
    finalHTML.append("<html><body>")
    finalHTML.append('<h3><font color="red">Deployment not accessible</font></h3>')
    finalHTML.append("<pre>")

    finalHTML.append(
        '<font color="red" size="4"><b>'
        + deploymenturl
        + " is not accessible</b></font>"
    )
    finalHTML.append(
        '<font color="blue"><br/>Please check: <a href="'
        + jenkinsurl
        + '">Test Report</a><br/>'
    )
    finalHTML.append("</pre></body></html>")

    with open("TeamHTML.html", "w") as filehandle:
        for listitem in finalHTML:
            filehandle.write("%s\n" % listitem)


def GetTestCaseMap(client, runID, testSuiteName, matchTestFileName):
    runs = runID.split(",")

    testcaseMap = {}
    testReportedMap = {}

    for id in runs:
        paginationOffsetGetTests = "&offset=0"
        print("TestRailID:" + str(id))
        while paginationOffsetGetTests:
            all_tests_in_run_response = client.send_get(
                "get_tests/" + str(id).strip() + "/" + paginationOffsetGetTests
            )
            for test in all_tests_in_run_response["tests"]:
                if matchTestFileName:
                    if (str(test["custom_testcasefile"])) == testSuiteName:
                        testcaseMap[str(test["custom_testcasename"])] = str(test["id"])
                else:
                    try:
                        testcaseMap[str(test["custom_testcasename"])] = str(test["id"])
                    except Exception as ex:
                        print(
                            "Error in Test Case Name: "
                            + str(test["custom_testcasename"])
                            + " - "
                            + str(ex)
                        )
                        testcaseMap[str(test["custom_testcasename"])] = str(test["id"])

            if all_tests_in_run_response["_links"]["next"] == None:
                paginationOffsetGetTests = all_tests_in_run_response["_links"]["next"]
            else:
                paginationOffsetGetTests = (
                    "&offset"
                    + all_tests_in_run_response["_links"]["next"].split("&offset")[1]
                )

    return testcaseMap


def SetTestStatus(client, caseNumber, status, comment):

    data = {}
    data["status_id"] = status
    data["comment"] = comment

    try:
        response = client.send_post("add_result/" + str(caseNumber), data)
    except Exception as Ex:
        print("Got Error reporting to TestRail ... skip and continue")


def get_build_info():
    with open("./build.json", "r") as j_file:
        build_info = json.load(j_file)
    return {
        "version": build_info["arcgis_version"],
        "build": build_info["arcgis_build"],
    }


if __name__ == "__main__":
    start = timer()

    # Required Parameters
    # 1. testrail username
    # 2. testrail password
    # 3. testrail Run Number
    # 4. JUnit result XML
    # 5. Version
    # 6. BUILD
    # 7. Jenkins URL
    # 8. Environment

    parser = argparse.ArgumentParser(
        description='Report JUnit Test Results from XML to TestRail. Either "-version & -build" OR'
        '"-serverurl, -serveruser and -serverpass" are required'
    )

    parser.add_argument(
        "-tu",
        dest="testrailuser",
        action="store",
        help="TestRail user name",
        default="enterprise-test-automation-team@esri.com",
    )
    parser.add_argument(
        "-tp",
        dest="testrailpass",
        action="store",
        help="TestRail password",
        default="tJB6Pkd3.mZv4UD",
    )
    parser.add_argument(
        "-tr",
        dest="testrailrun",
        action="store",
        required=True,
        help="TestRail Run Number. Multiple can be provided comma separated",
    )
    parser.add_argument(
        "-xml",
        dest="xml",
        action="store",
        required=True,
        help="JUnit XML file. Note if this file does not exist, all the Tests will be marked as "
        "Skipped on TestRails",
    )
    parser.add_argument(
        "-environment",
        dest="environment",
        action="store",
        required=True,
        default="Windows",
        help="Environment: Endeavour / Windows / Linux",
    )
    parser.add_argument(
        "-jenkins", dest="jenkins", action="store", help="Jenkins link to Test Result"
    )
    parser.add_argument(
        "-matchTestFileName",
        dest="matchTestFileName",
        action="store_true",
        help="[Optional] Set to True to match test file name. Defaults to False.",
    )

    args = parser.parse_args()

    build_info = get_build_info()

    client = Setup(vars(args)["testrailuser"], vars(args)["testrailpass"])

    version = build_info["version"]
    build = build_info["build"]
    jenkins = ""
    environment_name = ""
    suite_name = str(vars(args)["xml"]).split("/")[1]

    if "0000" in args.testrailrun.strip():
        print(
            "Dummy TestRails ID: "
            + str(vars(args)["testrailrun"])
            + " skip reporting to TestRails."
        )
        exit(0)

    try:
        if args.jenkins is None:
            jenkins = None
        else:
            jenkins = str(vars(args)["jenkins"])

        if args.environment:
            environment_name = str(vars(args)["environment"])

        print("Final Version: " + str(version))
        print("Final Build: " + str(build))
        print("Final Jenkins: " + str(jenkins))
        print("Final EnvironmentName: " + str(environment_name))
        print("Match Test File Name: " + str(args.matchTestFileName))

        file_list = []
        xml_file = vars(args)["xml"]
        if "*.xml" in xml_file:
            current_path = xml_file.replace("*.xml", "")
            if current_path != "":
                for file in os.listdir(current_path):
                    if file.endswith(".xml"):
                        file_list.append(os.path.join(current_path, file))
            else:
                for file in os.listdir():
                    if file.endswith(".xml"):
                        file_list.append(os.path.join(current_path, file))
        else:
            file_list.append(xml_file)

        print(file_list)
        for file in file_list:
            convertURL(
                client,
                file,
                True,
                vars(args)["testrailrun"],
                str(version),
                str(build),
                str(jenkins),
                str(environment_name),
                bool(args.matchTestFileName),
            )

        # # Maybe revisit this
        # CreateHTMLTableTestResult(
        #     str(build), str(vars(args)["jenkins"]), version, suite_name
        # )

    except Exception as ex:
        deploymentUrlGiven = ""
        print(ex)
        print("Creating Error Teams Notification")
        CreateErrorHTMLResult(vars(args)["jenkins"], deploymentUrlGiven)
    end = timer()
    print(end - start)
