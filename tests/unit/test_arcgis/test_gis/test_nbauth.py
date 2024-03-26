import os
import json
import tempfile
import unittest
from unittest import mock
from arcgis.gis._impl.nbauth import AESCipher, get_token

# from arcgis.gis._impl._decrypt_nbauth import get_token, AESCipher

CASES = (
    {
        "decryptedToken": "3fjwv9IMmI1try5Wm5txAG2wLaFJ3zkzU7KOCV5KqrfTkyanGGOF53unkdehk9dDvapiIE_l_7uLTNCUODHtA_jYTRQBGudOudN78mq2w5qS0ZFm2zz-F1W_i1BHOghpQfrqBtOPg7-cTuKxXmiFu2WUnTaCUOiJR-k7S3t7OriEt0xjiojjB9Pg7UyA7n_ffVsQv988w1-lnVeGwVTuc0tXOkM7rgiBo2y2UG1xK44.",
        "encryptedToken": "IzWO7rzBZdfJM2bHBdHoWQIUgIoTHA_rlAHp4CKlH_1kfGhjxlvQe-m58TDpLQT1muG_xFRwdSpnmbHHm1jWX1hEEAn4xS5KPJkxK7GvEcdCNgNNXX144vk92A9-uO2LfmXIDnuvi0K-MYjLsmWv9H-GTcRE0AdidzYAt-CMcqKnOTagNLiCU8v9Ms0XXH9brc4Z1tcfDhtKJJOMyYM_75_355Haya7xFwJ7Y9THbn2W1mHIk93ASFYxXAPit_oqON63KK6Q9E7BMy8tZlojtj9jCV1mkv_sunFOG3aHtMvF8WsMvTQ7z-uOZlt7Dk1O",
        "hostname": "8125eb3c2024",
        "privatePortalUrl": "https://a.com:7443/b",
    },
    {
        "decryptedToken": "cWhv7VV5jECHeM2ztMockun_PdBdmyE5z2A4wYCIc0HnpLrTrRMMxQQ7DM-E_qJfQiByWy_XW7KY2O2RHm91NG3f5iKyLG2nauRjfDY5mXwALLBi5kYlHHOIZm-Rl9w9_WpmcVlut0LecdzsqYitKPtzQGfPgc6xxGQxyuY7ZnExHkDc6NiDgg9MePzrwewuT6nloKliLGzRQXkx0U9mRDf88NYc5AnJBV7tc67XGWA.",
        "encryptedToken": "cyjPPrzwOMeQ88vGdaV6CWKo77fcLUZ8Bn2Brq_AIOYYqsDmCrw763KqTmlovrprncbSob83nHV8qZnDkUS1hxW44VpxG37D8d8kvW4c4iDzIturA7iSnld_mIzV8UunW-Otv3f9AHI-qcrryMXggrr2eUMJj7U3K--5GAivi6ZY0Ejwnhj5TO3i1tfpCeN4xSBds_Yl7MVTAMTolz_NIBplf1DWpz4Bqx_VA18jmVoYWiXzre5CMjxeasmmmy-iRElvPaQYC_slp2SD9MEN89cTf_JFMwOcH8YvZEkT7By6dYoG7rxQ-wNyV5o3iWio",
        "hostname": "b49c66c60519",
        "privatePortalUrl": "https://37.120.95.41:6443/arcgis",
    },
    {
        "decryptedToken": "s9SEghotaPKXsSGDweUa9ri3XADCsKGxjTvM0Hm1auCrGG4ssG0ZLiV5G2tOZpRZcTG1IMexWGEXURn8DHXsxmD6L2nspK1Q8ETCAKecmSkrBKBTZf8kNWJcRCZuVO3XxMRfpDqDXetEkoXfRzGBiUSm35P3sIc1C03VFkLpsY7fI4Hs86hCato-XD62zuRGFrWvCaurJLOj5HFUVdh8EsMWuYYjSTIz8zE49W5nELw.",
        "encryptedToken": "iLcxs4Aduzs95dwEQJzL4FxOLhcUUC-7l9lhIgdJu70GN2gJBBeMWzUY3XokMsk5Kx4uSIDlDG0_0pr_4VmZu0iUEM0EIL8kyTaAALTcufj0RM-wbUdHh0-tn6kuVkZhb72LWmNymMkE8jJVgsgE5S0R4teUOfUzaNbbPAmLgR5CY89sIY_wOCd2H6mIVJLNlVTKBCQbiSog9QEPrMAUY9pmypB17a64b3ZRr6fdnpHlJj1VP5Inu6wmiH6RYIgwXqZ_jsfUbcLWCp-3F84Wbph14iqrALuSymmbWH7dWBu3EPnQRBCWi4rfgkC0A7b7",
        "hostname": "3a717f1d8889",
        "privatePortalUrl": "https://some-really-long-arbitrary-hostname-the-quick-brown-fox-jumps-over-the-lazy-dog.com:7443/arcgis",
    },
    {
        "decryptedToken": "2aicPCle5fBGupIxB9GeDIgrgnl5MwGnKeYRbSWtpZJ3CMhwGp5HglcUYmi7IDArnwij8ccaLQv4gpCADnpFS8Mn9mnX2GChEwj07BoulwtfwUacWytkDf-PDZme0YxfsGPnPVG_EwXcwvDGW2iCmoJ7_n6vo2qDLWpfdpGghigC9-eEpEaeK9EugxenXktaZFrCuQjEZo3vbEiQtKCUF-PquGB7VIYKmhGhXayOXfQ.",
        "encryptedToken": "SA8pGF1samvo7nUaHBAkeCo751stRpzfFfb_LCEWOrdi7mGNJ3s6Cw-vKCKCqKm8iufYEx_jG1Ux5xdpiF6DzO45BEgYXPqtCifvWUaMlWQGtb8B1UxAWHsMmHCzOUOn-U_8LWQQNWdhT2ZPy5N10mY9YZ56Vj1bItQFnMOO0s2O-JoQugi2YIPedFVLekVFoZ0Sg3eumUzYa97KNhBq_Ak9jolvhKrspgwynUGamE9u3BvZ_R28x7kjxcMa54BvV9QE7F864UFvQs5QRxRYIb4xTBQ-WzCZG5Nb7d3lgY7wFyPBOYbdZNPqFLttujrt",
        "hostname": "96367e5f9a6b",
        "privatePortalUrl": "https://MAJOR-linux.ESRI.com:7443/arcgis",
    },
    {
        "decryptedToken": "2aicPCle5fBGupIxB9GeDIgrgnl5MwGnKeYRbSWtpZJ3CMhwGp5HglcUYmi7IDArnwij8ccaLQv4gpCADnpFS8Mn9mnX2GChEwj07BoulwtfwUacWytkDf-PDZme0YxfsGPnPVG_EwXcwvDGW2iCmoJ7_n6vo2qDLWpfdpGghigC9-eEpEaeK9EugxenXktaZFrCuQjEZo3vbEiQtKCUF-PquGB7VIYKmhGhXayOXfQ.",
        "encryptedToken": "SA8pGF1samvo7nUaHBAkeCo751stRpzfFfb_LCEWOrdi7mGNJ3s6Cw-vKCKCqKm8iufYEx_jG1Ux5xdpiF6DzO45BEgYXPqtCifvWUaMlWQGtb8B1UxAWHsMmHCzOUOn-U_8LWQQNWdhT2ZPy5N10mY9YZ56Vj1bItQFnMOO0s2O-JoQugi2YIPedFVLekVFoZ0Sg3eumUzYa97KNhBq_Ak9jolvhKrspgwynUGamE9u3BvZ_R28x7kjxcMa54BvV9QE7F864UFvQs5QRxRYIb4xTBQ-WzCZG5Nb7d3lgY7wFyPBOYbdZNPqFLttujrt",
        "hostname": "96367e5f9a6b",
        "privatePortalUrl": "https://major-linux.esri.com:7443/arcgis",
    },
)


class TestNBAuthLogic(unittest.TestCase):
    def test_cipher(self):
        cipher = AESCipher("abc123", "efg456")
        word = "TheMagicWordIsDiscoFries."
        encrpyted = cipher.encrypt(word)
        decrypted = cipher.decrypt(encrpyted)
        assert decrypted == word

    def test_case_0(self):
        """tests the various decryption test cases"""
        case = CASES[0]
        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        aescipher = AESCipher(private_portal_url.lower(), hostname.lower())
        assert aescipher.decrypt(encrypt_token) == decrypt_token

    def test_case_1(self):
        """tests the various decryption test cases"""
        case = CASES[1]
        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        aescipher = AESCipher(private_portal_url.lower(), hostname.lower())
        assert aescipher.decrypt(encrypt_token) == decrypt_token

    def test_case_2(self):
        """tests the various decryption test cases"""
        case = CASES[2]
        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        aescipher = AESCipher(private_portal_url.lower(), hostname.lower())
        assert aescipher.decrypt(encrypt_token) == decrypt_token

    def test_case_3(self):
        """tests the various decryption test cases"""
        case = CASES[3]
        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        aescipher = AESCipher(private_portal_url.lower(), hostname.lower())
        assert aescipher.decrypt(encrypt_token) == decrypt_token

    def test_case_4(self):
        """tests the various decryption test cases"""
        case = CASES[4]
        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        aescipher = AESCipher(private_portal_url.lower(), hostname.lower())
        assert aescipher.decrypt(encrypt_token) == decrypt_token

    def test_get_token_4(self):
        """test the get_token logic"""
        import socket

        case = CASES[4]

        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        json_template = {
            "encryptedToken": encrypt_token,
            "referer": "https://datascienceqa.esri.com/",
            "privatePortalUrl": private_portal_url,
            "publicPortalUrl": private_portal_url,
            "expiration": 10080,
        }
        fp = os.path.join(tempfile.gettempdir(), ".nbauth_test")
        with open(fp, "w") as writer:
            writer.write(json.dumps(json_template))
        with mock.patch("socket.gethostname", return_value=hostname):
            assert decrypt_token == get_token(fp)
        os.remove(fp)

    def test_get_token_3(self):
        """test the get_token logic"""
        import socket

        case = CASES[3]

        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        json_template = {
            "encryptedToken": encrypt_token,
            "referer": "https://datascienceqa.esri.com/",
            "privatePortalUrl": private_portal_url,
            "publicPortalUrl": private_portal_url,
            "expiration": 10080,
        }
        fp = os.path.join(tempfile.gettempdir(), ".nbauth_test")
        with open(fp, "w") as writer:
            writer.write(json.dumps(json_template))
        with mock.patch("socket.gethostname", return_value=hostname):
            assert decrypt_token == get_token(fp)
        os.remove(fp)

    def test_get_token_2(self):
        """test the get_token logic"""
        import socket

        case = CASES[2]

        encrypt_token = case["encryptedToken"]
        decrypt_token = case["decryptedToken"]
        hostname = case["hostname"]
        private_portal_url = case["privatePortalUrl"]
        json_template = {
            "encryptedToken": encrypt_token,
            "referer": "https://datascienceqa.esri.com/",
            "privatePortalUrl": private_portal_url,
            "publicPortalUrl": private_portal_url,
            "expiration": 10080,
        }
        fp = os.path.join(tempfile.gettempdir(), ".nbauth_test")
        with open(fp, "w") as writer:
            writer.write(json.dumps(json_template))
        with mock.patch("socket.gethostname", return_value=hostname):
            assert decrypt_token == get_token(fp)
        os.remove(fp)


if __name__ == "__main__":
    unittest.main()
