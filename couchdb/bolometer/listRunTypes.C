{
  gROOT->ProcessLine(".x $KDATA_ROOT/kdatabase/setupKJson.h");
  cout << endl;
  KCurl c; 
  c.Get("edwdbik.fzk.de:5984","edwdb/_design/bolorunconfig/_view/condition?group_level=1");
  
  string v = c.GetReturn();
  KJson *vr = KJson_Parse(v.c_str());
  KJson *rows = KJson_GetObjectItem(vr,"rows");
  
  cout << "Run Types: " << endl;
  for (int i = 0; i < KJson_GetArraySize(rows); i++){
    KJson *row = KJson_GetArrayItem(rows, i);
    KJson *key = KJson_GetObjectItem(row, "key");
    cout << KJson_GetArrayItem(key,0)->valuestring << endl;
  }
}