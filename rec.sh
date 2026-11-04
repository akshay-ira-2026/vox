set -e
cd ~/vox
export DISPLAY=:99
Xvfb :99 -screen 0 960x1080x24 >/dev/null 2>&1 &
XV=$!; sleep 2
for m in naive vox; do
  rm -rf /tmp/chr_vox
  google-chrome --no-sandbox --no-first-run --disable-gpu --disable-dev-shm-usage --user-data-dir=/tmp/chr_vox --kiosk --window-size=960,1080 --window-position=0,0 "file:///home/user/vox/demo/desk.html?m=$m" >/dev/null 2>&1 &
  CH=$!; sleep 6
  xdotool mousemove 480 900 click 1 || true
  python demo/drive.py $m 79
  kill $CH || true; pkill -f chr_vox || true; sleep 2
done
kill $XV || true
