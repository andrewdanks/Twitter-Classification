#!/bin/sh

echo "Creating arff file for 3.1"
python buildarff.py obama:twts/BarackObama.twt colbert:twts/StephenAtHome.twt kutcher:twts/aplusk.twt kardashian:twts/KimKardashian.twt tyson:twts/neiltyson.twt shakira:twts/shakira.twt 3.1.arff
echo "Done"
echo "Creating arff file for 3.2"
python buildarff.py spears:twts/britneyspears.twt bieber:twts/justinbieber.twt perry:twts/katyperry.twt gaga:twts/ladygaga.twt rihanna:twts/rihanna.twt swift:twts/taylorswift13.twt 3.2.arff
echo "Done"
echo "Creating arff file for 3.3"
python buildarff.py cbc:twts/CBCNews.twt cnn:twts/cnn.twt star:twts/torontostarnews.twt reuters:twts/Reuters.twt nytimes:twts/nytimes.twt onion:twts/TheOnion.twt 3.3.arff
echo "Done"
echo "Creating arff file for 3.4"
python buildarff.py news:twts/CBCNews.twt+twts/cnn.twt+twts/torontostarnews.twt+twts/Reuters.twt+twts/nytimes.twt+twts/TheOnion.twt pop:twts/taylorswift13.twt+twts/rihanna.twt+twts/ladygaga.twt+twts/katyperry.twt+twts/justinbieber.twt+twts/britneyspears.twt 3.4.arff
python buildarff.py -500 news:twts/CBCNews.twt+twts/cnn.twt+twts/torontostarnews.twt+twts/Reuters.twt+twts/nytimes.twt+twts/TheOnion.twt pop:twts/taylorswift13.twt+twts/rihanna.twt+twts/ladygaga.twt+twts/katyperry.twt+twts/justinbieber.twt+twts/britneyspears.twt 3.4_500.arff
echo "Done"
