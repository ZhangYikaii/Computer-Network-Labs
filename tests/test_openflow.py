import unittest 
from copy import deepcopy
from switchyard.lib.packet.openflow import *
from switchyard.lib.address import EthAddr, IPv4Address, SpecialIPv4Addr

class OpenflowPacketTests(unittest.TestCase):
    def testHello(self):
        hello = OpenflowHeader(OpenflowType.Hello, 0)
        self.assertEqual(hello.to_bytes(), b'\x01\x00\x00\x08\x00\x00\x00\x00')
        hello.xid = 42
        self.assertEqual(hello.to_bytes(), b'\x01\x00\x00\x08\x00\x00\x00\x2a')
        bval = hello.to_bytes()

        hello2 = OpenflowHeader(OpenflowType.Hello)
        hello2.from_bytes(bval)
        self.assertEqual(hello, hello2)
       
    def testSwitchFeatureRequest(self):
        featuresreq = OpenflowHeader(OpenflowType.FeaturesRequest, 0)
        self.assertEqual(featuresreq.to_bytes(), b'\x01\x05\x00\x08\x00\x00\x00\x00')

    def testSwitchFeatureReply(self):
        featuresreply = OpenflowSwitchFeaturesReply()
        featuresreply.dpid_low48 = EthAddr("00:01:02:03:04:05")
        featuresreply.dpid_high16 = b'\xab\xcd'
        p = OpenflowPhysicalPort(0, EthAddr("ab:cd:ef:ab:cd:ef"), "eth0")
        featuresreply.ports.append(p)
        xb = featuresreply.to_bytes()
        fr = OpenflowSwitchFeaturesReply()
        fr.from_bytes(xb)
        self.assertEqual(fr, featuresreply)

    def testEchoRequest(self):
        echoreq = OpenflowEchoRequest()        
        echoreq.data = b'\x01\x23\x45'
        b = echoreq.to_bytes()
        self.assertTrue(b.endswith(b'\x01\x23\x45'))
        another = OpenflowEchoRequest()
        another.from_bytes(b)
        self.assertEqual(echoreq, another)

    def testEchoReply(self):
        echorepl = OpenflowEchoReply()
        echorepl.data = b'\x01\x23\x45'
        b = echorepl.to_bytes()
        self.assertTrue(b.endswith(b'\x01\x23\x45'))
        another = OpenflowEchoRequest()
        another.from_bytes(b)
        self.assertEqual(echorepl, another)

    def testMatchStruct(self):
        m = OpenflowMatch()
        b = m.to_bytes()
        self.assertEqual(len(b), 40)

        m2 = OpenflowMatch()
        m2.from_bytes(b)
        self.assertEqual(m, m2)

        m.wildcard_all()
        m2.from_bytes(m.to_bytes())
        self.assertListEqual(['NwSrc:32','NwDst:32','All'], m2.wildcards) 

        m.reset_wildcards()
        m.add_wildcard(OpenflowWildcards.DlSrc)
        m.add_wildcard(OpenflowWildcards.DlDst)
        xlist = m.wildcards
        m2.from_bytes(m.to_bytes())
        self.assertListEqual(xlist, m2.wildcards)

    def testMatchOverlap(self):
        m = OpenflowMatch()
        self.assertTrue(m.overlaps(m))
        
    def testError(self):
        e = OpenflowError()
        e.errortype = OpenflowErrorType.HelloFailed
        e.errorcode = OpenflowHelloFailedCode.PermissionsError
        e.data = b'\xef' * 10
        b = e.to_bytes()
        self.assertEqual(b, b'\x00\x00\x00\x01' + b'\xef'*10)

        e.errortype = OpenflowErrorType.BadAction
        e.errorcode = OpenflowFlowModFailedCode.Overlap
        b = e.to_bytes()
        self.assertEqual(b, b'\x00\x02\x00\x01' + b'\xef'*10)

if __name__ == '__main__':
    unittest.main()