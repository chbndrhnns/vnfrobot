from pytest import fixture

from DockerController import DockerController
from testutils import Result
from . import path

from tools.archive import (Archive)
from tools.easy_docker import (DockerContainer)

test_container = 'goss-test'


@fixture
def controller():
    return DockerController(base_dir=path)


# https://github.com/jhidding/easy-docker.py

### Copy data to a volume
# docker run -v my-jenkins-volume:/data --name helper busybox true
# docker cp . helper:/data
# docker rm helper


def test_put_file_and_execute():
    sed_program = """# usage: sed -f rot13.sed
    y/abcdefghijklmnopqrstuvwxyz/nopqrstuvwxyzabcdefghijklm/
    y/ABCDEFGHIJKLMNOPQRSTUVWXYZ/NOPQRSTUVWXYZABCDEFGHIJKLM/
    """

    message = "Vf gurer nalobql BHG gurer?"

    with DockerContainer('busybox') as c:
        c.put_archive(
            Archive('w')
                .add_text_file('rot13.sed', sed_program)
                .add_text_file('input.txt', message)
                .close())

        c.run([
            '/bin/sh', '-c',
            "/bin/sed -f 'rot13.sed' < input.txt > output.txt"])

        secret = c.get_archive('output.txt').get_text_file('output.txt')

        print(secret)


def cleanup(d, containers):
    if containers is None:
        containers = []
    if isinstance(containers, str):
        containers = [containers]

    for container in containers:
        try:
            d.dispatch(['stop', container])
            d.dispatch(['rm', container])
        except AssertionError:
            pass


def test__create_container__pass(controller):
    controller.dispatch(['run', '-d', '-p', '12345:80', '--name', test_container, 'nginx'])
    cleanup(controller, test_container)


def test__run_sidecar__pass(controller):
    cleanup(controller, test_container)

    controller.dispatch(['run', '-d', '-p', '12345:80', '--name', test_container, 'nginx'])

    result = controller.run_sidecar(image='subfuzion/netcat', command='-z 127.0.0.1 12345 ; echo $?')
    cleanup(controller, test_container)

    assert result == Result.PASS


def test__list_containers__pass(controller):
    controller = DockerController(base_dir=path)

    result = controller.get_containers()

    assert len(result) > 0


def test__get_env(controller):
    cleanup(controller, test_container)

    controller.dispatch(['run', '-d', '-p', '12345:80', '--name', test_container, 'nginx'])
    env = controller.get_env(test_container)
    assert isinstance(env, list)
    assert [e for e in env if 'PATH' in e]

    cleanup(controller, test_container)

