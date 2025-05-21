total=1000
for i in $(seq 1 $total); do
  curl -s -o /dev/null -w "%{time_total}\n" \
    "REPLACE WITH YOUR API" >> times.txt

  # Progress bar
  percent=$((i * 100 / total))
  bar=$(printf "%-${percent}s" "#" | tr ' ' '#')
  printf "\rProgress: [%-100s] %d%%" "$bar" "$percent"
done

echo -e "\nDone."

p95=$(awk 'BEGIN{count=0}{a[count++]=$1}END{asort(a); print a[int(.95*count)]}' times.txt)
echo "p95 latency = ${p95}s"
