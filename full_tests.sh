#!/bin/sh

prompt="An astronaut in the jungle, blue-orange colour scheme"
CSV=perf.csv
G=$1 # A100 or other

T40="schnell merged dev"
T40C="schnell-compile merged-compile dev-compile"
T24="schnell-fp8 merged-fp8-4step merged-fp8 dev-fp8 dev-fp8-e5m2"
T24C="merged-fp8-4step-compile dev-fp8-e5m2-compile"
T16="schnell-fp8-16GB merged-fp8-4step-16GB merged-fp8-16GB dev-fp8-16GB dev-fp8-e5m2-16GB"
T12="" #"sayakpaul-dev-nf4-12GB"
T4="schnell-low merged-low dev-low"

if [ "$G" = "A100" ]; then
	for i in $T40 ; do
		./test_images.py -p -t test/$i/$G "$prompt" -n 1 -m $i --csv $CSV -T $G
	done

	for i in $T40C ; do
		./test_images.py -p -t test/$i/$G "$prompt" -n 3 -m $i --csv $CSV -T $G
	done
fi

for i in $T24 $T16 $T12 $T4 ; do
	./test_images.py -p -t test/$i/$G "$prompt" -n 1 -m $i --csv $CSV -T $G
done

for i in $T24C ; do
	./test_images.py -p -t test/$i/$G "$prompt" -n 3 -m $i --csv $CSV -T $G
done
