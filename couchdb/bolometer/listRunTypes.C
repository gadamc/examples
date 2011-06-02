{
  gROOT->ProcessLine(".x $KDATA_ROOT/kdatabase/setupKJson.h");
  
  KCurl c; 
  c.Get("edwdbik.fzk.de:5984","edwdb/_design/bolorunconfig/_view/condition?group_level=1");
  
  string v = c.GetReturn();
  KJson *vr = KJson_Parse(v.c_str());
  
  
  
}