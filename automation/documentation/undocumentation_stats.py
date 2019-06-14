import pickle

def get_undoc_stats(infile,outfile):
    
    classes_count = 0
    methods_count = 0
    functions_count = 0
    classes_str = ""
    functions_str = ""

    with open(infile,'rb') as f:
        undoc = pickle.load(f)
        for module, entities in undoc[0].items():
            for class_, methods in entities['classes'].items():
                if len(methods):
                    methods_count += len(methods)
                else:
                    classes_count += 1
                    classes_str += "\n----- " + class_

            functions_count += len(entities['funcs'])
            for function in entities['funcs']:
                functions_str += "\n----- " + function

    with open(outfile,'w') as f:
        f.write("Undocumented classes:   %4d" % classes_count)
        f.write(classes_str)
        f.write("\n")
        f.write("Undocumented methods:   %4d" % methods_count)
        f.write("\n")
        f.write("Undocumented functions: %4d" % functions_count) 
        f.write(functions_str)