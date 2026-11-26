import java.io.*;
import java.nio.file.*;
import java.security.*;
import java.security.cert.*;
import java.security.spec.*;
import java.util.*;
import com.android.apksig.*;
public class SignAndVerify {
  public static void main(String[] a) throws Exception {
    PrivateKey key=KeyFactory.getInstance("RSA").generatePrivate(new PKCS8EncodedKeySpec(Files.readAllBytes(Path.of(a[0]))));
    X509Certificate cert=(X509Certificate)CertificateFactory.getInstance("X.509").generateCertificate(new FileInputStream(a[1]));
    String fingerprint=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(cert.getEncoded()));
    if(!fingerprint.equals("d04ef2a865f8ed5ab8f98321be93ed2881eaa64f844fbaf480e18a8336620a72"))throw new Exception("Wrong certificate");
    var signer=new ApkSigner.SignerConfig.Builder("P36",key,List.of(cert)).build();
    new ApkSigner.Builder(List.of(signer)).setInputApk(new File(a[2])).setOutputApk(new File(a[3])).setMinSdkVersion(24).setV1SigningEnabled(false).setV2SigningEnabled(true).setV3SigningEnabled(true).setV4SigningEnabled(false).build().sign();
    for(int[] range:new int[][]{{24,27},{28,36}}){
      var r=new ApkVerifier.Builder(new File(a[3])).setMinCheckedPlatformVersion(range[0]).setMaxCheckedPlatformVersion(range[1]).build().verify();
      if(!r.isVerified() || (range[0]==24&&!r.isVerifiedUsingV2Scheme()) || (range[0]==28&&!r.isVerifiedUsingV3Scheme()))throw new Exception("Signature verification failed: "+r.getErrors());
      for(var c:r.getSignerCertificates())if(!Arrays.equals(c.getEncoded(),cert.getEncoded()))throw new Exception("Certificate mismatch");
    }
    System.out.println("PASS: P36 V2/V3 signatures verified SDK24-36");
  }
}
