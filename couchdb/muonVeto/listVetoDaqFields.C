{
  //gROOT->ProcessLine(".x $KDATA_ROOT/kdatabase/setupKJson.h");
  gSystem->Load("libkdatabase");
  KCurl c;
  c.Get("https://edwdbik.fzk.de:6984","muonvetohardwaremap/_design/map/_view/module?reduce=false&include_docs=true&limit=1");
  
  string view = c.GetReturn();
  KJson *viewreturn = KJson::Parse(view.c_str());
  KJson *rows = KJson::GetObjectItem(viewreturn,"rows");
  /*
  int numRows = KJson_GetArraySize(rows);
  
  if(numRows != 1 || numRows == 0){
    cout << "wierd... number of rows should be one." << endl;
    return numRows;
  }
  */
  KJson *row = KJson::GetArrayItem(rows, 0);
  KJson *doc = KJson::GetObjectItem(row,"doc");
  
  //here's how you print out the entire json object
  //cout << "Just printing out the document so you can see how that is done" << endl;
  //cout << KJson_Print(doc) << endl;
  
  //here's how you get a specific object from the doc object
  KJson *item = KJson::GetObjectItem(doc, "HV value");
  cout << item->key << " : " << item->valueint << endl;
  
  KJson *docitem = doc->child;
    
  while(docitem != 0){  //now transverse through the document... 
                   //this code was written already knowing a little bit about the structure of the document
                   //specificly, I knew that there weren't any nested arrays or objects in this document
                   //if you just want to print out the document, use KJson_Print(doc)
    
    if (docitem->type == 4 )  //4 = string type, 3 = number type, 6 = object type. I need to fix the code so that you don't have to memorize this...
      cout << docitem->key << " : " << docitem->valuestring << endl;
    
    if (docitem->type == 3 )
      cout << docitem->key << " : " << docitem->valuedouble << endl;
    
    else if(docitem->type == 6 ) {
      
      KJson *subitem = docitem->child;
      cout << docitem->key << endl;
      while(subitem != 0){
        cout << "    ";
        if(subitem->type == 4)
          cout << subitem->key << " : " << subitem->valuestring << endl;
        else if (subitem->type == 3)
          cout << subitem->key << " : " << subitem->valuedouble << endl;
     
        subitem = subitem->next;
      }
    }
   
    docitem = docitem->next;
  }
  
}
