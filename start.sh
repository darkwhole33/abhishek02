if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/darkwhole33/abhishek02.git /darkwhole33
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /darkwhole33
fi
cd /darkwhole33
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
