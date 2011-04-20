
#include "string"
#include <cstring>
#include <iostream>
#include <istream>
#include <curl/curl.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <yajl/yajl_parse.h>
#include <yajl/yajl_gen.h>

using namespace std;

struct couchReturn{
  string val;
};  //i'll use this structure to hold the return from couch

size_t checkCouchDBReturn(void *data, size_t size, size_t nmemb, void *userdata)
{
  yajl_handle hand;
  yajl_gen_config conf = { 0, "" };
  yajl_gen g = yajl_gen_alloc(&conf, NULL);
  yajl_status stat;  
  yajl_parser_config cfg = { 1, 1 };
  hand = yajl_alloc(NULL, &cfg, NULL, (void *) g);
  //now, in this example the 'callback' is NULL. One thing that I would do 
  //would be to write a callback for the strings and check to see if I get
  //and "error" in the string returned by couch. 
  //of course, you could just do a simple search on
  //the userdata for the string "error". that may be easier. 
  //so, here i will save this data in a local struct to access 
  //later if i want. 
  if(userdata != NULL){
    couchReturn *mdata = (couchReturn *)userdata;
    mdata->val = (const char* )data;
  }  //as an example, I save the data into my local structure
  
  stat = yajl_parse(hand, (const unsigned char*)data, size*nmemb);
  
  
  if (stat != yajl_status_ok &&  
      stat != yajl_status_insufficient_data)
  {
    //it would be totally crazy if this failed! it would mean that
    //couch didn't return a json document (or, i guess it could mean that
    //the couch server went down!
    unsigned char * str = yajl_get_error(hand, 1, (const unsigned char*)data, size*nmemb);
    cerr << str << endl;
    yajl_free_error(hand, str);
    
  }   
  unsigned int length = yajl_get_bytes_consumed(hand) +1;  //this tells us how much data was consumed

  yajl_free(hand); //free the handle
  
  return length;  //according to libcurl documentation, we are supposed to return this
}

size_t passJsonString(char *bufptr, size_t size, size_t nitems, void *userp)
{
  const char* mydata = (const char*)userp;
  memcpy(bufptr, mydata, size*nitems);
  return strlen(mydata);
}


int main(int /*argc*/, char** /*argv*/)
{
  //this example has three parts.
  //
  //1. First part shows how to use yajl to pack data into
  //a json format. however, its totally possible to do this yourself
  //
  //2. The second part shows how to initialize libcurl and to upload
  //a document. You have to set the read/write callback functions and data pointers
  //and you have to set the appropriate header
  //
  //3. The final part is just a quick demonstration of how to recycle 
  //a yajl generator, calling 'clear' and then 
  
  
 
  //yajl_handle hand;
  yajl_gen_config conf ={0, " " };  //if you set 0 -> 1, then it will print "pretty" json
  yajl_gen g; //this is the json generator
  yajl_gen_status status; //you can check the 'status' after each step
                      //look here for status return codes
                      //http://tinyurl.com/3d9duf9
                      //if you want to do some error checking.
  
  g = yajl_gen_alloc(&conf, NULL);  //load the configuration to the generator and allocate 
  
  status = yajl_gen_map_open(g);  //MUST start by opening a "map", which is the "{" character and starts the 
  
  int maxlen = 10000;  //some huge number of characters we won't exceed (hopefully!) 
  char key[maxlen]; 
  char value[maxlen];
  char id[maxlen];
  
  //one key value pair
  strncpy(key,"_id",maxlen);
  strncpy(id, "ld01a000_0_sambarunheader", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)id,strlen(id));
  
  strncpy(key,"author",maxlen);
  strncpy(value, "samba", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  strncpy(key,"type",maxlen);
  strncpy(value, "samba run header", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  //add a nested key/value pair for a particular key
  strncpy(key,"Bolo.reglages",maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  
  status = yajl_gen_map_open(g); //start nested key/value pairs that will be the 'value' for the key 'bolo.reglages'
  
  strncpy(key,"polar-centre",maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_integer(g,8);
  
  strncpy(key,"polar-garde",maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_double(g,-0.5);
  
  status = yajl_gen_map_close(g);  //end nested key/value pairs
  
   //more standard key/values
  strncpy(key,"Temperature",maxlen);
  yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  yajl_gen_double(g,0.020);
  
  strncpy(key,"run_name",maxlen);
  strncpy(value, "ld01a000", maxlen);
  yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  strncpy(key,"file_number",maxlen);
  yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  yajl_gen_integer(g,0);
  
  status = yajl_gen_map_close(g);  //finally close the document.
  
  if(status != yajl_gen_status_ok){
    cout << "hmmm some sort of error:" << status << endl;
  }
  
  
  //extract the json into a buffer in order to send it via libcurl
  const unsigned char * buf;
  unsigned int len;
  yajl_gen_get_buf(g, &buf, &len);
 
  cout << "here's the data that will be uploaded: " << endl << buf << endl;

  CURL *curlhandle;
  CURLcode res;
  
  couchReturn myReturn;
  
  curlhandle = curl_easy_init();
  char errorBuf[CURL_ERROR_SIZE + 100];
  
  if(curlhandle) {
    //string myurl = "http://michel:gros1234@http://134.158.176.27:5984/testdb/";
    string myurl = "http://cox:lepton@127.0.0.1:5984/testdb/";
    myurl.append(id);
    cout << "will call curl PUT " << myurl << endl;
    curl_easy_setopt(curlhandle, CURLOPT_URL, myurl.c_str());
    struct curl_slist *jsonheader = NULL;
    jsonheader = curl_slist_append(jsonheader, "Content-Type: application/json");
    curl_easy_setopt(curlhandle, CURLOPT_HTTPHEADER, jsonheader);

    curl_easy_setopt(curlhandle, CURLOPT_WRITEFUNCTION, checkCouchDBReturn); //catch the output from couch and deal with it
    curl_easy_setopt(curlhandle, CURLOPT_WRITEDATA, &myReturn);  //checkCouchDBReturn will pass the output to myReturn
    curl_easy_setopt(curlhandle, CURLOPT_READFUNCTION, passJsonString); //calls this function to get data
    curl_easy_setopt(curlhandle, CURLOPT_READDATA, buf);//passJsonString will get buffer data using this pointer
    curl_easy_setopt(curlhandle, CURLOPT_UPLOAD, 1); //upload the contents found in buf
    curl_easy_setopt(curlhandle, CURLOPT_INFILESIZE, len);  //the length of buf
    curl_easy_setopt(curlhandle, CURLOPT_ERRORBUFFER, errorBuf);
    res = curl_easy_perform(curlhandle);
    
    
    if(res){
      cout << "Error code: " << res << endl;
      cout << "Error: " << errorBuf << endl;
    }
    cout << "now what does my return value say?" << endl;
    cout << myReturn.val << endl;
    
    curl_easy_cleanup(curlhandle); //always cleanup
  }
    
  
  //start a new document
  yajl_gen_clear(g);  //clear the buffer when you're done. 
  conf.beautify = 1;  //make it look 'beautiful'
  g = yajl_gen_alloc(&conf, NULL);  //reload the configuration
  
  status = yajl_gen_map_open(g);//start a new map of keys/values
  strncpy(key,"run_name",maxlen);
  strncpy(value, "ld01a000", maxlen);
  yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  strncpy(key,"_id",maxlen);
  strncpy(id, "ld01a000_1_sambarunheader", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)id,strlen(id));
  
  strncpy(key,"author",maxlen);
  strncpy(value, "samba", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  strncpy(key,"type",maxlen);
  strncpy(value, "samba run header", maxlen);
  status = yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  status = yajl_gen_string(g,(const unsigned char*)value,strlen(value));
  
  strncpy(key,"file_number",maxlen);
  yajl_gen_string(g,(const unsigned char*)key,strlen(key));
  yajl_gen_integer(g,0);
  
  status = yajl_gen_map_close(g);  // close the document.
  
  
  yajl_gen_get_buf(g, &buf, &len);
  cout << endl;
  cout << "with beautiful config " << endl;
  cout << "here's what it looks like: " << endl << buf << endl;

  
  yajl_gen_clear(g);  //clear the buffer when you're done. 
  
  return 0;
}
