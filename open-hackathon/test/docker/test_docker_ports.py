import sys

sys.path.append("../src/hackathon")
from mock import Mock
import unittest
from hackathon.docker import OssDocker
from hackathon.database import db_adapter
from hackathon.database.models import DockerHostServer


class TestDocker(unittest.TestCase):
    @unittest.skip("not ready")
    def test_host_ports(self):
        mock_cache = Mock()
        mock_cache.host_ports = []
        for i in range(0, 29):
            OssDocker.host_ports.append(i)
            mock_cache.host_ports.append(i)
        mock_cache.host_ports.append(10001)
        docker1 = OssDocker()
        return_port = docker1.get_available_host_port(db_adapter.find_first_object_by(DockerHostServer, id=1), 1)
        self.assertEqual(10001, return_port)
        self.assertListEqual(mock_cache.host_ports, OssDocker.host_ports)

        docker2 = OssDocker()
        mock_cache.host_ports = [10002]
        return_port = docker2.get_available_host_port(db_adapter.find_first_object_by(DockerHostServer, id=1), 2)
        self.assertEqual(10002, return_port)
        self.assertListEqual(mock_cache.host_ports, OssDocker.host_ports)