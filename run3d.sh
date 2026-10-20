B=/opt/blender/blender-4.2.3-linux-x64/blender; cd /workspace/manzo_vainilla
s=$(date +%s)
RX=1080 SAMPLES=16 nice -n 15 $B -b -P render_3d.py -- 0 508 > /tmp/mv3d_log.txt 2>&1
RX=1080 SAMPLES=32 nice -n 15 $B -b -P render_3d.py -- thumb >> /tmp/mv3d_log.txt 2>&1
echo RENDER_SECONDS $(( $(date +%s)-s ))
