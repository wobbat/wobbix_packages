{ lib, stdenv, fetchurl, jdk17, runtimeShell, unzip, chromium }:

stdenv.mkDerivation rec {
  pname = "burp";
  version = "2023.1.2";
  
  src = fetchurl {
    name = "burp_pro.jar";
    urls = [
      "https://portswigger-cdn.net/burp/releases/download?product=pro&version=${version}&type=Jar"
    ];
    sha256 = "sha256-rM3xipN07Eg3aP6DnaWYMdAMAETv/3lF5CDjzBEF0nY=";
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
    exec ${jdk17}/bin/java -jar ${src} "$@"' > $out/bin/burp
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
    platforms = jdk17.meta.platforms;
    license = licenses.unfree;
    hydraPlatforms = [];
    maintainers = with maintainers; [ stoek ];
  };
}
