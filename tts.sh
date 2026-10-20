V=/workspace/piper_voices
i=0
while IFS='|' read who txt; do
 m=$V/es_MX-ald-medium.onnx; [ "$who" = N ] && m=$V/es_MX-claude-high.onnx
 echo "$txt" | piper -m $m --length_scale 1.05 -f l$i.wav 2>/dev/null; i=$((i+1))
done < script.txt
