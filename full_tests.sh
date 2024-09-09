#!/bin/sh

folder="$1"
G="$2" # A100 or other
prompt="cool street art of an astronaut in a jungle, stencil and spray paint style, the flag says 'FLUX.1', on a door in a graffiti covered alley scene with used spray paint cans littering the ground, a sign by the door says 'Open' in faded, yellowed, black and white plastic, the secret door to a great club, the other writing says 'matatonic', 'flux.1 2024', 'black forest labs', 'openedai' and 'uNStaBLe' in unique styles"
CSV="$folder/perf.csv"

T40="dall-e-3 schnell merged dev"
T40C="schnell-compile merged-compile dev-compile"
T24="schnell-fp8 merged-fp8-4step merged-fp8 dev-fp8"
T24C="schnell-fp8-compile merged-fp8-4step-compile merged-fp8-compile dev-fp8-compile"
T16="schnell-fp8-16GB merged-fp8-4step-16GB merged-fp8-16GB dev-fp8-16GB"
T12="" #"sayakpaul-dev-nf4-12GB"
T4="schnell-low merged-low dev-low"

if [ "$G" = "A100" ]; then
	for i in $T40 ; do
		./test_images.py -p -t $folder/$i/$G "$prompt" -n 1 -m "$i" --csv "$CSV" -T $G
	done

	for i in $T40C ; do
		./test_images.py -p -t "$folder/$i/$G" "$prompt" -n 3 -m "$i" --csv "$CSV" -T $G
	done
fi

for i in $T24 $T16 $T12 $T4 ; do
	./test_images.py -p -t "$folder/$i/$G" "$prompt" -n 1 -m "$i" --csv "$CSV" -T $G
done

for i in $T24C ; do
	./test_images.py -p -t "$folder/$i/$G" "$prompt" -n 3 -m "$i" --csv "$CSV" -T $G
done
