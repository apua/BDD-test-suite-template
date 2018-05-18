uri = {
    # ------------------------------------
    # Atlas URIs
    # ------------------------------------
    'eula_save': "/rest/appliance/eula/save",
    'network_interfaces': "/rest/appliance/network-interfaces",
    'login_sessions': "/rest/login-sessions",
    'users': "/rest/users",
    'user_role': "/rest/users/role",
    'change_password': "/rest/users/changePassword",
    'roles': "/rest/roles",
    'task': '/rest/tasks',
    # ------------------------------------
    #  Firmware Upgrade
    # ------------------------------------
    'upload_image': '/rest/appliance/firmware/image',
    'install_image': '/rest/appliance/firmware/pending?file=',
    'upgrade_status': '/rest/appliance/firmware/notification',
    # ------------------------------------
    #  Abort Jobs
    # ------------------------------------
    'abort_grace':'/clean',
    'abort_imm':'/fast',
    # ------------------------------------
    #  Backup/Restore
    # ------------------------------------
    'backup_config': '/rest/cirrus/backup_restore_settings/backup',
    'start_backup': '/rest/cirrus/backup_restore_settings/start_backup',
    # ------------------------------------
    #  Hardware
    # ------------------------------------
    'hardware':'/rest/cirrus/servers',
    'hardware_group':'/rest/cirrus/hardware/hierarchy',
    'export_hardware':'/rest/cirrus/export_hardware',
    'import_hardware':'/rest/cirrus/import_hardware',
    'add_import_hardware':'/rest/cirrus/add_import_hardware',
    # ------------------------------------
    #  Test plans
    # ------------------------------------
    'testplan': '/rest/cirrus/testplans/jcfs',
    'export_testplan': '/rest/cirrus/testplans/export_testplan',
    'import_testplan': '/rest/cirrus/testplans/import_testplan',
    'jobs': '/rest/cirrus/jobs'
}
# dev_nfs address in Taipei lab
DEV_NFS="10.30.1.60"
nfs_user="devnfs"
nfs_pw="Compaq123"


