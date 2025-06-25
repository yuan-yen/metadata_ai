

# Install ffmpeg
INSTALL_DIR="/usr/local/bin"
FFMPEG_URL="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
curl -L "$FFMPEG_URL" -o /tmp/ffmpeg.tar.xz
mkdir -p /tmp/ffmpeg-static
tar -xf /tmp/ffmpeg.tar.xz -C /tmp/ffmpeg-static --strip-components=1
sudo cp /tmp/ffmpeg-static/ffmpeg /tmp/ffmpeg-static/ffprobe "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/ffmpeg" "$INSTALL_DIR/ffprobe"
rm -rf /tmp/ffmpeg.tar.xz /tmp/ffmpeg-static
ffmpeg -version


#curl -lk https://packages.microsoft.com/yumrepos/vscode/Packages/c/code-1.96.4-1736991167.el8.x86_64.rpm  -o /tmp/code.rpm
#sudo dnf install /tmp/code.rpm -y
