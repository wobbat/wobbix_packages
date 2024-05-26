import os
import urllib.request
import subprocess
import re
import string

# URL of the JAR file
JAR_URL = "https://portswigger-cdn.net/burp/releases/download?product=pro&type=Jar"

# Function to download the JAR file
def download_jar(url):
    try:
        with urllib.request.urlopen(url) as response:
            content_disposition = response.getheader('Content-Disposition')
            if content_disposition and 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('\"')
            else:
                print("Could not determine filename from Content-Disposition header.")
                exit(1)
            
            with open(filename, 'wb') as file:
                file.write(response.read())
        print(f"Downloaded {filename} from {url}")
        return filename
    except Exception as e:
        print(f"Failed to download the JAR file: {e}")
        exit(1)

# Function to run the nix-hash command and get the hash
def get_nix_hash(filename):
    try:
        result = subprocess.run(
            ['nix-hash', '--flat', '--base32', '--type', 'sha256', filename],
            check=True, capture_output=True, text=True
        )
        hash_value = result.stdout.strip()
        print(f"nix-hash command executed successfully with output:\n{hash_value}")
        return hash_value
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the nix-hash command on {filename}: {e}")
        exit(1)

# Function to extract version from filename
def extract_version(filename):
    match = re.search(r'burpsuite_pro_v(\d+\.\d+\.\d+\.\d+)\.jar', filename)
    if match:
        version = match.group(1)
        print(f"Extracted version: {version}")
        return version
    else:
        print("Could not extract version from filename.")
        exit(1)

# Function to create the Nix expression file
def create_nix_file(version, hash_value):
    nix_content = """
{ lib, stdenv, fetchurl, jdk17, runtimeShell, unzip, chromium }:

stdenv.mkDerivation rec {
  pname = "burp";
  version = "{version}";
  
  src = fetchurl {
    name = "burp_pro.jar";
    urls = [
      "https://portswigger-cdn.net/burp/releases/download?product=pro&type=Jar"
    ];
    sha256 = "sha256-{hash_value}";
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
"""

    # template = string.Template(nix_content)
    # modified_string = template.safe_substitute({
    # "{version}": version,
    # "{hash_value}": hash_value
    # })
    nix_content = nix_content.replace("{version}", version)
    nix_content = nix_content.replace("{hash_value}", hash_value)
    with open('pkgs/burp-pro/default.nix', 'w') as file:
        file.write(nix_content)
    print("Nix file created successfully.")

# Main script execution
def main():
    filename = download_jar(JAR_URL)
    hash_value = get_nix_hash(filename)
    version = extract_version(filename)
    create_nix_file(version, hash_value)
    
    # Remove the JAR file
    try:
        os.remove(filename)
        print(f"Removed {filename}")
    except OSError as e:
        print(f"Failed to remove the JAR file {filename}: {e}")
        exit(1)

if __name__ == "__main__":
    main()
