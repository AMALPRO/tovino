if [ -z $UPSTREAM_REPO ]
then
  echo "Cloning main Repository"
  git clone https://github.com/AMALPRO/tovinox.git /tovinox
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO "
  git clone $UPSTREAM_REPO /tovinox
fi
cd /tovinox
pip3 install -U -r requirements.txt
echo "Starting Tovix...."
python3 bot.py
