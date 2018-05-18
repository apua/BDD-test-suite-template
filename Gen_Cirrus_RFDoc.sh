#!/bin/sh
python -m robot.libdoc resources/EsxiLib.py::10.30.1.79::root::Compaq123 EsxiLib.html
python -m robot.libdoc resources/CirrusRESTLib.py::VM CirrusRESTLib.html
python -m robot.libdoc resources/selenium_wrapper.txt Cirrus_GUI_Selenium.html
python -m robot.libdoc resources/config/env_setup.txt GUI_Env_Setup.html
python -m robot.libdoc resources/fixtures/fixture_and_faker.txt Fixtures.html
python -m robot.libdoc resources/VerifyResults.py VerifyResults.html
zip Cirrus_RFDoc.zip EsxiLib.html CirrusRESTLib.html Cirrus_GUI_Selenium.html GUI_Env_Setup.html Fixtures.html VerifyResults.html
