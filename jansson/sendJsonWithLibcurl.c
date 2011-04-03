#include <jansson.h>
#include <curl/curl.h>
#include <cstdio>
#include <cstring>
#include <cstdlib>

#define BUFFER_SIZE (256 * 1024) //256 kb. initila buffer size. 

using namespace std;

struct write_result  //use this struct to store the result from a curl call
{
  int len; 
  char *data;
  int pos;
};

size_t passJsonDoc(char *bufptr, size_t size, size_t nitems, void *userp)
{
  json_t * mydata = (json_t *)userp;
  char *buf = json_dumps(mydata , JSON_INDENT(0))
  memcpy(bufptr, buf, strlen(buf);
  return strlen(buf);
}

static size_t handleJsonReturn(void *ptr, size_t size, size_t nmemb, void *data)
{
  struct write_result *result = (struct write_result *)data;
  
  if(result->pos + size * nmemb >= len - 1)
  {
    free(result->data);
    result->data = (char*)malloc((size*nmemb+1)*sizeof(char));
  }
  //this is done because curl can return data in chunks instead of 
  //full strings. so we have to keep track of where we have to 
  //add to the data string. 
  memcpy(result->data + result->pos, ptr, size * nmemb);
  result->pos += size * nmemb;
  
  return size * nmemb;
}

int main (int argc, char** argv)
{

  //create json document
  
  json_t *doc = json_object();
  
  json_object_set_new(doc, "_id", json_string(argv[5]));
  json_object_set_new(doc, "author", json_string("samba"));
  json_object_set_new(doc, "type", json_string("samba run header"));
  json_object_set_new(doc, "Temperature", json_real(0.02002));
  json_object_set_new(doc, "Year", json_integer(2011));
  
  //add a subdoc (a nested set of key/value pairs) to doc
  json_t *subdoc = json_object();
  json_object_set_new(subdoc, "polar-centre", json_real(4.0));
  json_object_set_new(subdoc, "polar-garde", json_real(1.5));
  json_object_set(doc, "Bolo.reglages", subdoc);
  json_decref(subdoc);  //have to deal with the garbage collector
  
  //add an array to doc
  json_t *array = json_array();
  json_array_append(array, json_integer(2011));
  json_array_append(array, json_integer(4));
  json_array_append(array, json_integer(2));
  json_object_set(doc, "Date", array);
  json_decref(array); //deal with garbage collector
                  
  //print out the json document just to check it
  printf("\n%s\n\n",json_dumps(doc, JSON_INDENT(2)));  //the 2 option tells the output to use indentation to make it look "pretty"
  
  
  //now send the json document to the server with libcurl
  CURL *curlhandle;
  CURLcode res;
    
  char data[BUFFER_SIZE];
  write_result myresult;
  myresult.data = data;  //create a write_result and set the pointer to allocated space.
  myresult.len = BUFFER_SIZE;
  
  curlhandle = curl_easy_init();
  char errorBuf[CURL_ERROR_SIZE + 100];
    
  if(curlhandle) {
  
    char myurl[1000];
    json_t *id = json_object_get(doc,"_id");
    if(id== NULL){
      printf("error. no id\n");
      return -1;  //only send a document that has the _id key, otherwise couch will create an id for you. 
    }

    sprintf(myurl, "http://%s:%s@%s/%s/%s", argv[3], argv[4], argv[1], argv[2], json_string_value(id));
    printf("will call curl PUT %s\n\n", myurl);
    
    curl_easy_setopt(curlhandle, CURLOPT_URL, myurl);
    
    //use appropriate json header for curl
    struct curl_slist *jsonheader = NULL;
    jsonheader = curl_slist_append(jsonheader, "Content-Type: application/json");
    curl_easy_setopt(curlhandle, CURLOPT_HTTPHEADER, jsonheader);
    
    //set the curl options for this transaction
    curl_easy_setopt(curlhandle, CURLOPT_WRITEFUNCTION, handleJsonReturn); //catch the output from couch and deal with it with this function
    curl_easy_setopt(curlhandle, CURLOPT_WRITEDATA, &myresult);  //checkCouchDBReturn will pass the output to myReturn
    curl_easy_setopt(curlhandle, CURLOPT_READFUNCTION, passJsonDoc); //calls this function to get data to PUT to the couchdb server
    curl_easy_setopt(curlhandle, CURLOPT_READDATA, doc);//passJsonString will get buf data using this pointer
    curl_easy_setopt(curlhandle, CURLOPT_UPLOAD, 1); //tell curl to upload the contents that passJsonString tells it to.
    curl_easy_setopt(curlhandle, CURLOPT_INFILESIZE, len);  //the length of buf that will be PUT
    curl_easy_setopt(curlhandle, CURLOPT_ERRORBUFFER, errorBuf);  //hold any errors here.
    curl_easy_setopt(curlhandle, CURLOPT_VERBOSE, 1);
   
    //perform the transaction
    res = curl_easy_perform(curlhandle);
    //check for errors
    if(res){ //if res == 0, everything went well
      printf("Error code: %u \n", res);
      printf("Error: %s\n\n",errorBuf);
    }
    
    //now read the return from the curl call, which is stored
    //in myresult and pass it to the json parser, which will 
    //unpack the string into a json_t object.
    json_error_t jsonerror;
    json_t *root = json_loads(myresult.data, 0, &jsonerror);
    
    if(json_is_object(root))
      printf("%s\n\n",json_dumps(root, JSON_INDENT(0)));  //print the return as pretty json
      
    else {
      printf("didn't get a json object back from the curl call");
    }

    curl_easy_cleanup(curlhandle); //always cleanup curl handles
    
  }
  
  curl_global_cleanup();
  return 0;

}
