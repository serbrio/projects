#!/bin/bash
# Command line version of the game Mastermind or Code Braker
# or alson known as "Byki i korovy".

echo ===============================================
echo Biky i korovy
echo
echo Rules.
echo "Given: code *****"
echo The code contains five of the following digits:
echo 12345678
echo One digit can appear in the code only once.
echo Guess the right digits and their correct order. 
echo You have 8 attempts.
echo
echo "Your result will be printed in the format:"
echo "++O--"
echo "This result would mean: 3 digits guessed,"
echo "two of them are on correct places."
echo -----------------------------------------------
echo "+ is a guessed digit on it's correct place"
echo "O is a guessed digit not on correct place"
echo ===============================================
echo


byki_i_korovy () {
	code=$( shuf -e 1 2 3 4 5 6 7 8 | head -n 5 | tr -d '[:space:]' )
	counter=1
	#echo Code: $code ##
	echo "Enter digits without spaces. Example: 12345"
	
	while [ $counter -le  8 ]
	do
		echo 
		echo Attempt No: $counter
		read -p "Enter: " guess
		
		# check length(guess) == 5
		# and check guess is digits from 1 to 8
		if [ ! "$( echo $guess | grep '^[1-8]\{5\}$' )"  ]
		then
			echo 
			echo "! Please enter 5 digits from 1 to 8"
			continue
		fi

		if [ $guess == $code ]
		then
			echo
			echo "+++++"
			echo Congratulations! You got it!
			echo Your guess:  $guess
			echo The code is: $code
			break
		fi
		
		guessed_digits=0
		correct_order=0
		result=""
		
		for index in {0..4}
		do
			if [ ${guess:$index:1} == ${code:$index:1} ]
			then
				(( correct_order++ ))
			fi
		done
		
		uniques=$( for index in {0..4}; do echo ${guess:$index:1}; done | uniq )
		#echo "Uniques: $uniques" ##

		for digit in $uniques
		do
			if [ "$(echo $code | grep  $digit)" ]
			then
				(( guessed_digits++ ))
			fi
		done

		#echo Guessed digits: $guessed_digits
		#echo On correct places: $correct_order
		
		c_signs=${correct_order}
		g_signs=$(( $guessed_digits - $correct_order ))
		dot_signs=$(( 5 - $guessed_digits  ))
		#echo "ordered: $c_signs"
		#echo "guessed: $g_signs"
		#echo "dots:    $dot_signs"
		result=""

		for i in $( seq 1 $c_signs )
		do
			result=${result}'+'
		done

		for i in $( seq 1 $g_signs )
		do
			result=${result}'O'
		done

		for i in $( seq 1 $dot_signs )
		do
			result=${result}'-'
		done
		
		echo $result
		
		case "$counter" in
			"8")
				echo ==================================
				echo Cheer up!
				echo The code was: $code
				echo Try again!
				echo ===================================
				;;
		esac

		(( counter++ ))
	done
}


actions="Try Quit"
PS3='Select what to do: 1) Try and 2) Quit. -> '

select action in $actions
do
	if [ $action == "Quit" ]
	then
		break
	fi
	byki_i_korovy
done

echo
echo Have a nice day!