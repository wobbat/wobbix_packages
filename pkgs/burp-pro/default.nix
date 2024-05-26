
{ lib, stdenv, fetchurl, jdk21, runtimeShell, unzip, chromium }:

stdenv.mkDerivation rec {
  pname = "burp";
  version = "2024.3.1.4_fix";
  
  src = fetchurl {
    name = "burp_pro.jar";
    urls = [
      "https://portswigger-cdn.net/burp/releases/download?product=pro&type=Jar"
    ];
    sha256 = "sha256-ABteovdl3/VBfxyHtOHSI3Er2mupvGCmSmxsCqPMW18=";
  };

  dontUnpack = true;
  dontBuild = true;
  installPhase = ''
    runHook preInstall

    mkdir -p $out/bin
    echo '#!${runtimeShell}
    eval "$(${unzip}/bin/unzip -p ${src} chromium.properties)"
    mkdir -p "$HOME/.BurpSuite/burpbrowser/$linux64"
    ln -sf "${chromium}/bin/chromium" "$HOME/.BurpSuite/burpbrowser/$linux64/chrome"
    exec ${jdk21}/bin/java -jar ${src} "$@"' > $out/bin/burp
    chmod +x $out/bin/burp

    runHook postInstall
  '';

  preferLocalBuild = true;

  meta = with lib; {
    description = "An integrated platform for performing security testing of web applications";
    longDescription = ''
      Burp Suite is an integrated platform for performing security testing of web applications.
      Its various tools work seamlessly together to support the entire testing process, from
      initial mapping and analysis of an application's attack surface, through to finding and
      exploiting security vulnerabilities.
    '';
    homepage = "https://portswigger.net/burp/";
    downloadPage = "https://portswigger.net/burp/freedownload";
    platforms = jdk21.meta.platforms;
    # license = licenses.unfree;
    hydraPlatforms = [];
    maintainers = with maintainers; [ wobbat ];
  };
}
