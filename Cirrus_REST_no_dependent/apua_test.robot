*** Settings ***
Resource    apua_common.robot

Suite setup     login
Suite teardown  logout

*** test cases ***
TC
    api.t
TC 1
    api.t
