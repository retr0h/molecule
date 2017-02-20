#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import collections
import os

import pytest

from molecule import config
from molecule import util
from molecule.provisioner import ansible


@pytest.fixture
def molecule_provisioner_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'config_options': {
                'defaults': {
                    'foo': 'bar'
                },
            },
            'connection_options': {
                'foo': 'bar'
            },
            'options': {
                'foo': 'bar'
            },
            'env': {
                'foo': 'bar'
            },
            'host_vars': {
                'instance-1': [{
                    'foo': 'bar'
                }],
                'localhost': [{
                    'foo': 'baz'
                }]
            },
            'group_vars': {
                'example_group1': [{
                    'foo': 'bar'
                }],
                'example_group2': [{
                    'foo': 'bar'
                }],
            }
        },
    }


@pytest.fixture
def ansible_instance(molecule_provisioner_section_data, config_instance):
    config_instance.merge_dicts(config_instance.config,
                                molecule_provisioner_section_data)

    return ansible.Ansible(config_instance)


def test_config_private_member(ansible_instance):
    assert isinstance(ansible_instance._config, config.Config)


def test_default_config_options_property(ansible_instance):
    libraries_directory = ansible_instance._get_libraries_directory()
    filter_plugins_directory = ansible_instance._get_filter_plugin_directory()
    x = {
        'defaults': {
            'ansible_managed':
            'Ansible managed: Do NOT edit this file manually!',
            'retry_files_enabled': False,
            'host_key_checking': False,
            'nocows': 1,
            'roles_path': '../../../../:$ANSIBLE_ROLES_PATH',
            'library': '{}:$ANSIBLE_LIBRARY'.format(libraries_directory),
            'filter_plugins':
            '{}:$ANSIBLE_FILTER_PLUGINS'.format(filter_plugins_directory),
        },
        'ssh_connection': {
            'ssh_args': '-o UserKnownHostsFile=/dev/null',
            'scp_if_ssh': True,
        },
    }

    assert x == ansible_instance.default_config_options


def test_default_options_property(ansible_instance):
    assert {} == ansible_instance.default_options


def test_default_env_property(ansible_instance):
    x = ansible_instance._config.provisioner.config_file

    assert x == ansible_instance.default_env['ANSIBLE_CONFIG']
    assert 'MOLECULE_FILE' in ansible_instance.default_env
    assert 'MOLECULE_INVENTORY_FILE' in ansible_instance.default_env
    assert 'MOLECULE_SCENARIO_DIRECTORY' in ansible_instance.default_env
    assert 'MOLECULE_INSTANCE_CONFIG' in ansible_instance.default_env


def test_name_property(ansible_instance):
    assert 'ansible' == ansible_instance.name


def test_config_options_property(ansible_instance):
    libraries_directory = ansible_instance._get_libraries_directory()
    filter_plugins_directory = ansible_instance._get_filter_plugin_directory()
    x = {
        'defaults': {
            'ansible_managed':
            'Ansible managed: Do NOT edit this file manually!',
            'retry_files_enabled': False,
            'host_key_checking': False,
            'nocows': 1,
            'roles_path': '../../../../:$ANSIBLE_ROLES_PATH',
            'library': '{}:$ANSIBLE_LIBRARY'.format(libraries_directory),
            'filter_plugins':
            '{}:$ANSIBLE_FILTER_PLUGINS'.format(filter_plugins_directory),
            'foo': 'bar'
        },
        'ssh_connection': {
            'ssh_args': '-o UserKnownHostsFile=/dev/null',
            'scp_if_ssh': True,
        },
    }

    assert x == ansible_instance.config_options


def test_options_property(ansible_instance):
    x = {'foo': 'bar'}

    assert x == ansible_instance.options


def test_options_property_handles_cli_args(ansible_instance):
    ansible_instance._config.args = {'debug': True}

    assert ansible_instance.options['vvv']


def test_env_property(ansible_instance):
    x = ansible_instance._config.provisioner.config_file

    assert x == ansible_instance.env['ANSIBLE_CONFIG']
    assert 'bar' == ansible_instance.env['foo']


def test_host_vars_property(ansible_instance):
    x = {'instance-1': [{'foo': 'bar'}], 'localhost': [{'foo': 'baz'}]}

    assert x == ansible_instance.host_vars


def test_group_vars_property(ansible_instance):
    x = {
        'example_group1': [{
            'foo': 'bar'
        }],
        'example_group2': [{
            'foo': 'bar'
        }]
    }

    assert x == ansible_instance.group_vars


def test_inventory_property(ansible_instance):
    x = {
        'ungrouped': {
            'vars': {}
        },
        'bar': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        },
        'foo': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                },
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        },
        'baz': {
            'hosts': {
                'instance-2-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        }
    }

    assert x == ansible_instance.inventory


def test_inventory_property_handles_missing_groups(temp_dir, ansible_instance):
    platforms = [{'name': 'instance-1'}, {'name': 'instance-2'}]
    ansible_instance._config.config['platforms'] = platforms

    x = {
        'ungrouped': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'vars': {}
        }
    }

    assert x == ansible_instance.inventory


def test_inventory_file_property(ansible_instance):
    x = os.path.join(ansible_instance._config.ephemeral_directory,
                     'ansible_inventory.yml')

    assert x == ansible_instance.inventory_file


def test_config_file_property(ansible_instance):
    x = os.path.join(ansible_instance._config.ephemeral_directory,
                     'ansible.cfg')

    assert x == ansible_instance.config_file


def test_playbooks_setup_property(ansible_instance):
    x = os.path.join(ansible_instance._config.scenario.directory, 'create.yml')

    assert x == ansible_instance.playbooks.setup


@pytest.fixture
def molecule_provisioner_playbooks_driver_section_data():
    return {
        'provisioner': {
            'name': 'ansible',
            'playbooks': {
                'docker': {
                    'setup': 'docker-create.yml',
                    'converge': 'docker-playbook.yml',
                    'teardown': 'docker-destroy.yml',
                },
                'setup': 'create.yml',
                'converge': 'playbook.yml',
                'teardown': 'destroy.yml',
            },
        }
    }


def test_playbooks_setup_property_when_driver(
        molecule_provisioner_playbooks_driver_section_data, ansible_instance):
    ansible_instance._config.merge_dicts(
        ansible_instance._config.config,
        molecule_provisioner_playbooks_driver_section_data)
    x = os.path.join(ansible_instance._config.scenario.directory,
                     'docker-create.yml')

    assert x == ansible_instance.playbooks.setup


def test_playbooks_converge_property(ansible_instance):
    x = os.path.join(ansible_instance._config.scenario.directory,
                     'playbook.yml')

    assert x == ansible_instance.playbooks.converge


def test_playbooks_converge_property_when_driver(
        molecule_provisioner_playbooks_driver_section_data, ansible_instance):
    ansible_instance._config.merge_dicts(
        ansible_instance._config.config,
        molecule_provisioner_playbooks_driver_section_data)
    x = os.path.join(ansible_instance._config.scenario.directory,
                     'docker-playbook.yml')

    assert x == ansible_instance.playbooks.converge


def test_playbooks_teardown_property(ansible_instance):
    x = os.path.join(ansible_instance._config.scenario.directory,
                     'destroy.yml')

    assert x == ansible_instance.playbooks.teardown


def test_playbooks_teardown_property_when_driver(
        molecule_provisioner_playbooks_driver_section_data, ansible_instance):
    ansible_instance._config.merge_dicts(
        ansible_instance._config.config,
        molecule_provisioner_playbooks_driver_section_data)
    x = os.path.join(ansible_instance._config.scenario.directory,
                     'docker-destroy.yml')

    assert x == ansible_instance.playbooks.teardown


def test_connection_options(ansible_instance):
    x = {'ansible_connection': 'docker', 'foo': 'bar'}

    assert x == ansible_instance.connection_options('foo')


def test_add_or_update_vars(ansible_instance):
    ephemeral_directory = ansible_instance._config.ephemeral_directory

    host_vars_directory = os.path.join(ephemeral_directory, 'host_vars')
    host_vars = os.path.join(host_vars_directory, 'instance-1-default')

    ansible_instance.add_or_update_vars('host_vars')
    assert os.path.isdir(host_vars_directory)
    assert os.path.isfile(host_vars)

    host_vars_localhost = os.path.join(host_vars_directory, 'localhost')
    assert os.path.isfile(host_vars_localhost)

    group_vars_directory = os.path.join(ephemeral_directory, 'group_vars')
    group_vars_1 = os.path.join(group_vars_directory, 'example_group1')
    group_vars_2 = os.path.join(group_vars_directory, 'example_group2')

    ansible_instance.add_or_update_vars('group_vars')
    assert os.path.isdir(group_vars_directory)
    assert os.path.isfile(group_vars_1)
    assert os.path.isfile(group_vars_2)


def test_add_or_update_vars_does_not_create_vars(ansible_instance):
    ansible_instance._config.config['provisioner']['host_vars'] = {}
    ansible_instance._config.config['provisioner']['group_vars'] = {}
    ephemeral_directory = ansible_instance._config.ephemeral_directory

    host_vars_directory = os.path.join(ephemeral_directory, 'host_vars')
    group_vars_directory = os.path.join(ephemeral_directory, 'group_vars')

    ansible_instance.add_or_update_vars('host_vars')
    ansible_instance.add_or_update_vars('group_vars')

    assert not os.path.isdir(host_vars_directory)
    assert not os.path.isdir(group_vars_directory)


def test_check(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.check()

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        ansible_instance._config.provisioner.playbooks.converge,
        ansible_instance._config, )
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_converge(ansible_instance, mocker, patched_ansible_playbook):
    result = ansible_instance.converge()

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        ansible_instance._config.provisioner.playbooks.converge,
        ansible_instance._config, )
    assert result == 'patched-ansible-playbook-stdout'

    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_converge_with_playbook(ansible_instance, mocker,
                                patched_ansible_playbook):
    result = ansible_instance.converge('playbook')

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        'playbook',
        ansible_instance._config, )
    assert result == 'patched-ansible-playbook-stdout'

    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_destroy(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.destroy()

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        ansible_instance._config.provisioner.playbooks.teardown,
        ansible_instance._config, )
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_setup(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.setup()

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        ansible_instance._config.provisioner.playbooks.setup,
        ansible_instance._config, )
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_syntax(ansible_instance, mocker, patched_ansible_playbook):
    ansible_instance.syntax()

    inventory_file = ansible_instance._config.provisioner.inventory_file
    patched_ansible_playbook.assert_called_once_with(
        inventory_file,
        ansible_instance._config.provisioner.playbooks.converge,
        ansible_instance._config, )
    patched_ansible_playbook.return_value.add_cli_arg.assert_called_once_with(
        'syntax-check', True)
    patched_ansible_playbook.return_value.execute.assert_called_once_with()


def test_write_inventory(temp_dir, ansible_instance):
    ansible_instance.write_inventory()

    assert os.path.isfile(ansible_instance.inventory_file)

    data = util.safe_load_file(ansible_instance.inventory_file)

    x = {
        'ungrouped': {
            'vars': {}
        },
        'bar': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        },
        'foo': {
            'hosts': {
                'instance-1-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                },
                'instance-2-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child1': {
                    'hosts': {
                        'instance-1-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                },
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        },
        'baz': {
            'hosts': {
                'instance-2-default': {
                    'ansible_connection': 'docker',
                    'foo': 'bar'
                }
            },
            'children': {
                'child2': {
                    'hosts': {
                        'instance-2-default': {
                            'ansible_connection': 'docker',
                            'foo': 'bar'
                        }
                    }
                }
            }
        }
    }

    assert x == data


def test_write_config(temp_dir, ansible_instance):
    ansible_instance.write_config()

    assert os.path.isfile(ansible_instance.config_file)


def test_verify_inventory(ansible_instance):
    ansible_instance._verify_inventory()


def test_verify_inventory_raises_when_missing_hosts(
        temp_dir, patched_logger_critical, ansible_instance):
    ansible_instance._config.config['platforms'] = []
    with pytest.raises(SystemExit) as e:
        ansible_instance._verify_inventory()

    assert 1 == e.value.code

    msg = "Instances missing from the 'platform' section of molecule.yml."
    patched_logger_critical.assert_called_once_with(msg)


def test_vivify(ansible_instance):
    d = ansible_instance._vivify()
    d['bar']['baz'] = 'qux'

    assert 'qux' == str(d['bar']['baz'])


def test_default_to_regular(ansible_instance):
    d = collections.defaultdict()
    assert isinstance(d, collections.defaultdict)

    d = ansible_instance._default_to_regular(d)
    assert isinstance(d, dict)


def test_get_plugin_directory(ansible_instance):
    result = ansible_instance._get_plugin_directory()
    parts = pytest.helpers.os_split(result)

    assert ('molecule', 'provisioner', 'ansible', 'plugins') == parts[-4:]


def test_get_libraries_directory(ansible_instance):
    result = ansible_instance._get_libraries_directory()
    parts = pytest.helpers.os_split(result)
    x = ('molecule', 'provisioner', 'ansible', 'plugins', 'libraries')

    assert x == parts[-5:]


def test_get_filter_plugin_directory(ansible_instance):
    result = ansible_instance._get_filter_plugin_directory()
    parts = pytest.helpers.os_split(result)
    x = ('molecule', 'provisioner', 'ansible', 'plugins', 'filters')

    assert x == parts[-5:]
