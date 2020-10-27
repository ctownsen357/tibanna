import os
import pytest
from awsf3.prerun_utils import (
    create_env_def_file,
    create_mount_command_list,
    create_download_command_list,
    add_download_cmd
)
from tibanna.awsem import AwsemRunJson, AwsemRunJsonInput


def test_create_env_def_file_cwl():
    """testing create_env_def_file with cwl option and an input Env variable"""
    envfilename = 'someenvfile'

    runjson_dict = {'Job': {'App': {'cwl_url': 'someurl',
                                    'main_cwl': 'somecwl',
                                    'other_cwl_files': 'othercwl1,othercwl2'},
                            'Input': {'Env': {'SOME_ENV': '1234'}},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'cwl')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export CWL_URL=someurl\n'
                     'export MAIN_CWL=somecwl\n'
                     'export CWL_FILES="othercwl1 othercwl2"\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export SOME_ENV=1234\n'
                     'export PRESERVED_ENV_OPTION="--preserve-environment SOME_ENV "\n'
                     'export DOCKER_ENV_OPTION="-e SOME_ENV "\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_env_def_file_wdl():
    """testing create_env_def_file with wdl option and no input Env variable"""
    envfilename = 'someenvfile'

    runjson_dict = {'Job': {'App': {'wdl_url': 'someurl',
                                    'main_wdl': 'somewdl',
                                    'other_wdl_files': 'otherwdl1,otherwdl2'},
                            'Input': {'Env': {}},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'wdl')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export WDL_URL=someurl\n'
                     'export MAIN_WDL=somewdl\n'
                     'export WDL_FILES="otherwdl1 otherwdl2"\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export PRESERVED_ENV_OPTION=""\n'
                     'export DOCKER_ENV_OPTION=""\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_env_def_file_shell():
    """testing create_env_def_file with shell option and two input Env variables"""
    envfilename = 'someenvfile'

    runjson_dict = {'Job': {'App': {'command': 'com1;com2',
                                    'container_image': 'someimage'},
                            'Input': {'Env': {'ENV1': '1234', 'ENV2': '5678'}},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'shell')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export COMMAND="com1;com2"\n'
                     'export CONTAINER_IMAGE=someimage\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export ENV1=1234\n'
                     'export ENV2=5678\n'
                     'export PRESERVED_ENV_OPTION="--preserve-environment ENV1 --preserve-environment ENV2 "\n'
                     'export DOCKER_ENV_OPTION="-e ENV1 -e ENV2 "\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_env_def_file_shell2():
    """testing create_env_def_file with shell option with complex commands and an env variable"""
    envfilename = 'someenvfile'

    complex_command = 'echo $SOME_ENV | xargs -i echo {} > somedir/somefile'
    runjson_dict = {'Job': {'App': {'command': complex_command,
                                    'container_image': 'someimage'},
                            'Input': {'Env': {'SOME_ENV': '1234'}},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'shell')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export COMMAND="echo $SOME_ENV | xargs -i echo {} > somedir/somefile"\n'
                     'export CONTAINER_IMAGE=someimage\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export SOME_ENV=1234\n'
                     'export PRESERVED_ENV_OPTION="--preserve-environment SOME_ENV "\n'
                     'export DOCKER_ENV_OPTION="-e SOME_ENV "\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_env_def_file_shell3():
    """testing create_env_def_file with shell option with complex commands and an env variable.
    double-quotes are escaped when written to the env file ('"' -> '\"')"""
    envfilename = 'someenvfile'

    complex_command = 'echo "haha" > somefile; ls -1 [st]*'
    runjson_dict = {'Job': {'App': {'command': complex_command,
                                    'container_image': 'someimage'},
                            'Input': {'Env': {}},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'shell')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export COMMAND="echo \\"haha\\" > somefile; ls -1 [st]*"\n'
                     'export CONTAINER_IMAGE=someimage\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export PRESERVED_ENV_OPTION=""\n'
                     'export DOCKER_ENV_OPTION=""\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_env_def_file_snakemake():
    """testing create_env_def_file with shell option and two input Env variables"""
    envfilename = 'someenvfile'

    runjson_dict = {'Job': {'App': {'command': 'com1;com2',
                                    'container_image': 'someimage',
                                    'snakemake_url': 'someurl',
                                    'main_snakemake': 'somecwl',
                                    'other_snakemake_files': 'othercwl1,othercwl2'},
                            'Input': {},
                            'Output': {'output_bucket_directory': 'somebucket'}},
                    'config': {'log_bucket': 'somebucket'}}
    runjson = AwsemRunJson(**runjson_dict)
    create_env_def_file(envfilename, runjson, 'shell')

    with open(envfilename, 'r') as f:
        envfile_content = f.read()

    right_content = ('export COMMAND="com1;com2"\n'
                     'export CONTAINER_IMAGE=someimage\n'
                     'export OUTBUCKET=somebucket\n'
                     'export PUBLIC_POSTRUN_JSON=0\n'
                     'export PRESERVED_ENV_OPTION=""\n'
                     'export DOCKER_ENV_OPTION=""\n')

    assert envfile_content == right_content
    os.remove(envfilename)


def test_create_mount_command_list():
    mountcommand_filename = 'some_mountcommand_filename'
    rji_dict = {'arg1': {'path': 'somefile', 'dir': 'somebucket', 'mount': True},
                'arg2': {'path': 'somefile2', 'dir': 'somebucket', 'mount': True},
                'arg3': {'path': 'whatever', 'dir': 'do_not_mount_this_bucket', 'mount': False},
                'arg4': {'path': 'somefile3', 'dir': 'somebucket2', 'mount': True}}
    runjson_input = AwsemRunJsonInput(**{'Input_files_data': rji_dict})
    create_mount_command_list(mountcommand_filename, runjson_input)
    
    with open(mountcommand_filename, 'r') as f:
        mcfile_content = f.read()

    right_content = ('mkdir -p /data1/input-mounted-somebucket\n'
                     'goofys-latest -f somebucket /data1/input-mounted-somebucket &\n'
                     'mkdir -p /data1/input-mounted-somebucket2\n'
                     'goofys-latest -f somebucket2 /data1/input-mounted-somebucket2 &\n')

    assert mcfile_content == right_content
    os.remove(mountcommand_filename)


def test_create_download_command_list_args():
    dl_command_filename = 'some_dlcommand_filename'
    rji_dict = {'arg1': {'path': 'somefile', 'dir': 'somebucket', 'mount': False},
                'arg2': {'path': 'somefile2.gz', 'dir': 'somebucket', 'mount': False, 'unzip': 'gz'},
                'arg3': {'path': 'whatever', 'dir': 'mount_this_bucket', 'mount': True},
                'arg4': {'path': 'somefile3', 'dir': 'somebucket2', 'mount': False}}
    runjson_input = AwsemRunJsonInput(**{'Input_files_data': rji_dict})
    create_download_command_list(dl_command_filename, runjson_input, 'cwl')

    with open(dl_command_filename, 'r') as f:
        dcfile_content = f.read()

    right_content = ('if [[ -z $(aws s3 ls s3://somebucket/somefile/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile /data1/input/somefile ;  '
                     'else aws s3 cp --recursive s3://somebucket/somefile /data1/input/somefile ;  fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket/somefile2.gz/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile2.gz /data1/input/somefile2.gz ; '
                     'gunzip /data1/input/somefile2.gz; '
                     'else aws s3 cp --recursive s3://somebucket/somefile2.gz /data1/input/somefile2.gz ; '
                     'for f in `find /data1/input/somefile2.gz -type f`; do if [[ $f =~ \.gz$ ]]; then gunzip $f; fi; done; fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket2/somefile3/ ) ]]; then '
                     'aws s3 cp s3://somebucket2/somefile3 /data1/input/somefile3 ;  '
                     'else aws s3 cp --recursive s3://somebucket2/somefile3 /data1/input/somefile3 ;  fi\n')

    assert dcfile_content == right_content
    os.remove(dl_command_filename)


def test_create_download_command_list_args_rename():
    dl_command_filename = 'some_dlcommand_filename'
    rji_dict = {'arg1': {'path': 'somefile', 'dir': 'somebucket', 'mount': False, 'rename': 'renamed_file'},
                'arg2': {'path': 'somefile2.gz', 'dir': 'somebucket', 'mount': False, 'unzip': 'gz'},
                'arg3': {'path': 'whatever', 'dir': 'mount_this_bucket', 'mount': True},
                'arg4': {'path': 'somefile3', 'dir': 'somebucket2', 'mount': False, 'rename': 'renamed_file2'}}
    runjson_input = AwsemRunJsonInput(**{'Input_files_data': rji_dict})
    create_download_command_list(dl_command_filename, runjson_input, 'cwl')

    with open(dl_command_filename, 'r') as f:
        dcfile_content = f.read()

    right_content = ('if [[ -z $(aws s3 ls s3://somebucket/somefile/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile /data1/input/renamed_file ;  '
                     'else aws s3 cp --recursive s3://somebucket/somefile /data1/input/renamed_file ;  fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket/somefile2.gz/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile2.gz /data1/input/somefile2.gz ; '
                     'gunzip /data1/input/somefile2.gz; '
                     'else aws s3 cp --recursive s3://somebucket/somefile2.gz /data1/input/somefile2.gz ; '
                     'for f in `find /data1/input/somefile2.gz -type f`; do if [[ $f =~ \.gz$ ]]; then gunzip $f; fi; done; fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket2/somefile3/ ) ]]; then '
                     'aws s3 cp s3://somebucket2/somefile3 /data1/input/renamed_file2 ;  '
                     'else aws s3 cp --recursive s3://somebucket2/somefile3 /data1/input/renamed_file2 ;  fi\n')

    assert dcfile_content == right_content
    os.remove(dl_command_filename)


def test_create_download_command_list_file_uri_cwl_wdl_error():
    dl_command_filename = 'some_dlcommand_filename'
    rji_dict = {'file:///data1/input/file1': {'path': 'somefile', 'dir': 'somebucket', 'mount': False}}
    runjson_input = AwsemRunJsonInput(**{'Input_files_data': rji_dict})
    with pytest.raises(Exception) as ex:
        create_download_command_list(dl_command_filename, runjson_input, 'cwl')
    assert 'argument name for CWL' in str(ex)
    with pytest.raises(Exception) as ex:
        create_download_command_list(dl_command_filename, runjson_input, 'wdl')
    assert 'argument name for CWL' in str(ex)


def test_create_download_command_list_file_uri():
    dl_command_filename = 'some_dlcommand_filename'
    rji_dict = {'file:///data1/input/file1': {'path': 'somefile', 'dir': 'somebucket', 'mount': False},
                'file:///data1/input/file2.gz': {'path': 'somefile2.gz', 'dir': 'somebucket', 'mount': False, 'unzip': 'gz'},
                'file:///data1/input/haha': {'path': 'whatever', 'dir': 'mount_this_bucket', 'mount': True},
                'file:///data1/input/file3': {'path': 'somefile3', 'dir': 'somebucket2', 'mount': False}}
    runjson_input = AwsemRunJsonInput(**{'Input_files_data': rji_dict})
    create_download_command_list(dl_command_filename, runjson_input, 'shell')

    with open(dl_command_filename, 'r') as f:
        dcfile_content = f.read()

    right_content = ('if [[ -z $(aws s3 ls s3://somebucket/somefile/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile /data1/input/file1 ;  '
                     'else aws s3 cp --recursive s3://somebucket/somefile /data1/input/file1 ;  fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket/somefile2.gz/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile2.gz /data1/input/file2.gz ; '
                     'gunzip /data1/input/file2.gz; '
                     'else aws s3 cp --recursive s3://somebucket/somefile2.gz /data1/input/file2.gz ; '
                     'for f in `find /data1/input/file2.gz -type f`; do if [[ $f =~ \.gz$ ]]; then gunzip $f; fi; done; fi\n'
                     'if [[ -z $(aws s3 ls s3://somebucket2/somefile3/ ) ]]; then '
                     'aws s3 cp s3://somebucket2/somefile3 /data1/input/file3 ;  '
                     'else aws s3 cp --recursive s3://somebucket2/somefile3 /data1/input/file3 ;  fi\n')

    assert dcfile_content == right_content
    os.remove(dl_command_filename)


def test_add_download_cmd_profile():
    dl_command_filename = 'some_dlcommand_filename'
    f = open(dl_command_filename, 'w')
    add_download_cmd('somebucket', 'somefile', 'sometarget', '--profile user1', f, '')
    f.close()

    with open(dl_command_filename, 'r') as f:
        dcfile_content = f.read()

    right_content = ('if [[ -z $(aws s3 ls s3://somebucket/somefile/ --profile user1) ]]; then '
                     'aws s3 cp s3://somebucket/somefile sometarget --profile user1;  '
                     'else aws s3 cp --recursive s3://somebucket/somefile sometarget --profile user1;  fi\n')

    assert dcfile_content == right_content


def test_add_download_cmd_unzip_bz2():
    dcfile_content = add_download_cmd('somebucket', 'somefile.bz2', 'sometarget.bz2', '', None, 'bz2')
    right_content = ('if [[ -z $(aws s3 ls s3://somebucket/somefile.bz2/ ) ]]; then '
                     'aws s3 cp s3://somebucket/somefile.bz2 sometarget.bz2 ; '
                     'bzip2 -d sometarget.bz2; '
                     'else aws s3 cp --recursive s3://somebucket/somefile.bz2 sometarget.bz2 ; '
                     'for f in `find sometarget.bz2 -type f`; do if [[ $f =~ \.bz2$ ]]; then bzip2 -d $f; fi; done; fi\n')
    assert dcfile_content == right_content
