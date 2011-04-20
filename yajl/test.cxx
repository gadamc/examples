#include "string"
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


/*** default yajl example stuff **/

static int reformat_null(void * ctx)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_null(g);
  return 1;
}

static int reformat_boolean(void * ctx, int boolean)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_bool(g, boolean);
  return 1;
}

static int reformat_number(void * ctx, const char * s, unsigned int l)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_number(g, s, l);
  return 1;
}

static int reformat_string(void * ctx, const unsigned char * stringVal,
                           unsigned int stringLen)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_string(g, stringVal, stringLen);
  return 1;
}

static int reformat_map_key(void * ctx, const unsigned char * stringVal,
                            unsigned int stringLen)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_string(g, stringVal, stringLen);
  return 1;
}

static int reformat_start_map(void * ctx)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_map_open(g);
  return 1;
}


static int reformat_end_map(void * ctx)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_map_close(g);
  return 1;
}

static int reformat_start_array(void * ctx)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_array_open(g);
  return 1;
}

static int reformat_end_array(void * ctx)
{
  yajl_gen g = (yajl_gen) ctx;
  yajl_gen_array_close(g);
  return 1;
}

static yajl_callbacks callbacks = {
  reformat_null,
  reformat_boolean,
  NULL,
  NULL,
  reformat_number,
  reformat_string,
  reformat_start_map,
  reformat_map_key,
  reformat_end_map,
  reformat_start_array,
  reformat_end_array
};

/**  end default yajl stuff **/

struct MyStructure {
  string val;
  string jsonval;
};



size_t writeCallback(void *data, size_t size, size_t nmemb, void *userdata)
{
  yajl_handle hand;
  yajl_gen_config conf = { 1, "  " };
  yajl_gen g;
  yajl_status stat;
  /* allow comments */
  yajl_parser_config cfg = { 1, 1 };
  g = yajl_gen_alloc(&conf, NULL);
  hand = yajl_alloc(&callbacks, &cfg, NULL, (void *) g);
  
  cout << (const unsigned char*)data << endl;
  MyStructure *mdata = (MyStructure *)userdata;
  mdata->val = (const char*)data;
  
  stat = yajl_parse(hand, (const unsigned char*)data, size*nmemb);
  
  
  if (stat != yajl_status_ok &&
      stat != yajl_status_insufficient_data)
  {
    unsigned char * str = yajl_get_error(hand, 1, (const unsigned char*)data, size*nmemb);
    cerr << str << endl;
    yajl_free_error(hand, str);
    
  } else {
    cout << "there was no error" << endl;
    const unsigned char * buf;
    unsigned int len;
    yajl_gen_get_buf(g, &buf, &len);
    mdata->jsonval = (const char*)buf;
    cout << "pretty json: " << buf << endl;
    cout << " was length: " << len << endl;
    yajl_gen_clear(g);
  }
  
  yajl_free(hand);
  
  return size*nmemb;
}



int main(int argc, char** argv)
{
 
  CURL *curl;
  CURLcode res;
  
  
  MyStructure aStruct;
  char errorBuf[CURL_ERROR_SIZE+1];  //use this buffer to save any curl errors.

  curl = curl_easy_init();
  if(curl) {
    curl_easy_setopt(curl, CURLOPT_URL, "http://127.0.0.1:5984");
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &aStruct);
    curl_easy_setopt(curl, CURLOPT_ERRORBUFFER, errorBuf);  //hold any errors here.

    res = curl_easy_perform(curl);
    cout << "the curl return : " << res << endl;
    //check for errors
    if(res){ //if res == 0, everything went well
      printf("Curl returned an error.\n");
      printf("Error code: %u \n", res);
      printf("Error: %s\n\n",errorBuf);
    }

    
    cout << "now what does my return value say?" << endl;
    cout << aStruct.val << endl;
    cout << aStruct.jsonval << endl;
    
    /* always cleanup */ 
    curl_easy_cleanup(curl);
  }
  return 0;
}

