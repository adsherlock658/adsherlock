## AdSherlock

An efficient and deployable click fraud detection approach at the client side (inside the application) for mobile apps.  

The *src/adsherlock* directory contains the main implementation code, while the *example* directory has an example apk as well as its traffic file. The *FraudBench* contains two fraudulent programs for testing.

For a more detailed description and the design consideration, please refer to our paper. 

If you have any problems or interesting questions, please contact Chenhong at caoch@shu.edu.cn or submit an issue to our GitHub repository.



#### Offline Pattern Generation

 The offline pattern extractor automatically generates traffic patterns of ad and non-ad traffics for each app. The network traffics can be captured through `tcpdump` or other packet sniffing tools and stored in  `.pcap` file.  Then we need to parse these pcap files and extract features for the preliminary classification. These functions are implemented by  *requesttree.py* under *adsherlock/requestCap*. You can generate request tree as well as other page features used for request classification like so:   

```
python requesttree.py com.shoujiduoduo.ringtone
```

Next, we generate **exact patterns** and **probabilistic patterns**  for robust ad request identification.  You can try this out as follows:

```
python tokengenration.py /example/com.shoujiduoduo.ringtone/
```

The generated patterns are stored in the pattern file `com.shoujiduoduo.ringtone_pattern.txt`.

#### Online Fraud Detection

The core code of this part (Binary instrumentation, Network traffic interception, and Motion events collection) is currently in commercial cooperation with a company.  We plan to open source after the cooperation is over, with the permission of the company.

We implemented a simple simulation tool in Python to let the user experience the performance when running on the phone. 



#### FraudBench

We implement `ClickDroid` as a simple click bot to simulate the bot-driven fraudulent scenario. We also implement a simple application to simulate in-app fraudulent scenario. The simple application employs `performClick` method to generate click events for ads displayed automatically.  These two fraudulent programs are placed under */FraudBench/*.