#!/usr/bin/env bash

set -e

echo
echo "------------------------------------------"
echo "  Welcome aboard BEA! "
echo "------------------------------------------"
echo

echo 'Which browser do you wish to fly today? Enter 1 or 2. '

browser_options=("chrome" "firefox")

select opt in "${browser_options[@]}"; do
  case ${opt} in
  "chrome")
    browser="chrome"
    break
    ;;
  "firefox")
    browser="firefox"
    break
    ;;
  *)
    echo "Sorry, we don't have that browser in our fleet"
    exit 1
    ;;
  esac
done

headless_options=("regular" "headless")

select opt in "${headless_options[@]}"; do
  case ${opt} in
  "headless")
    headless=true
    break
    ;;
  "regular")
    headless=false
    break
    ;;
  *)
    echo "Sorry, we only have headless and non-headless cabins on our aircraft"
    exit 1
    ;;
  esac
done

echo
echo "Enter snippet (e.g., 'authorized_user' or 'curated_admits') that matches your destination today"
echo "Blank will fly you around the world, but we might run out of fuel"; echo
echo -n "    > "

read test_suite

echo
echo "Enter your username if required for your destination"
echo
printf "    > "

read -s username

echo
echo "Enter your password if required for your destination"
echo
printf "    > "

read -s password

echo
echo "Fasten your seatbelts and extinguish your cigarettes, we're off to ${test_suite}!"

test_suite="*${test_suite}*"
USERNAME="${username}" PASSWORD="${password}" pytest tests/test_${test_suite}.py --browser ${browser} --headless ${headless}

exit 0
