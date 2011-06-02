{
  gROOT->ProcessLine(".x $KDATA_ROOT/kdatabase/setupKJson.h");
  
  KCurl c;
  c.Get("edwdbik.fzk.de:5984","edwdb/_design/muonveto/_view/daqmap?reduce=false&include_docs=true&limit=1");
  
  string view = c.GetReturn();
  KJson *viewreturn = KJson_Parse(view.c_str());
  KJson *rows = KJson_GetObjectItem(viewreturn,"rows");
  /*
  int numRows = KJson_GetArraySize(rows);
  
  if(numRows != 1 || numRows == 0){
    cout << "wierd... number of rows should be one." << endl;
    return numRows;
  }
  */
  KJson *row = KJson_GetArrayItem(rows, 0);
  KJson *doc = KJson_GetObjectItem(row,"doc");
  
  //here's how you print out the entire json object
  //cout << "Just printing out the document so you can see how that is done" << endl;
  //cout << KJson_Print(doc) << endl;
  
  //here's how you get a specific object from the doc object
  KJson *item = KJson_GetObjectItem(doc, "HV value");
  cout << item->key << " : " << item->valueint << endl;
  
  KJson *docitem = doc->child;
    
  while(docitem != 0){  //now transverse through the document... 
                   //this code was written already knowing a little bit about the structure of the document
                   //specificly, I knew that there weren't any nested arrays or objects in this document
                   //if you just want to print out the document, use KJson_Print(doc)
    
    if (docitem->type == KJson_String )
      cout << docitem->key << " : " << docitem->valuestring << endl;
    
    if (docitem->type == KJson_Number )
      cout << docitem->key << " : " << docitem->valuedouble << endl;
    
    else if(docitem->type ==KJson_Object ) {
      
      KJson *subitem = docitem->child;
      cout << docitem->key << endl;
      while(subitem != 0){
        cout << "    ";
        if(subitem->type == KJson_String)
          cout << subitem->key << " : " << subitem->valuestring << endl;
        else if (subitem->type == KJson_Number)
          cout << subitem->key << " : " << subitem->valuedouble << endl;
     
        subitem = subitem->next;
      }
    }
   
    docitem = docitem->next;
  }
  
}