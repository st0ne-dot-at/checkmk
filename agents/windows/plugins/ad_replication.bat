@echo off

REM ***
REM * Following information concerns only Windows Server <2012R2
REM *
REM * To be able to run this check you need appropriate credentials
REM * in the target domain.
REM *
REM * Normally the Check_MK agent runs as sevice with local system
REM * credentials which are not enough for this check.
REM *
REM * To solve this problem you can do e.g. the following:
REM *
REM * - Change the account the service is being started with to a
REM *   domain user account with enough permissions on the DC.
REM *
REM ***

where /Q repadmin > nul
if ERRORLEVEL 1 goto SERVER_NOT_IN_DC_LIST
echo ^<^<^<ad_replication^>^>^>
repadmin /showrepl /csv
:SERVER_NOT_IN_DC_LIST
