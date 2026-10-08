/* Handy Glass & Door — Google tag + lead tracking.
   Google Ads: AW-16544169892. Add a GA4 ID (G-XXXX) to GA4_ID to also send to Analytics. */
(function(){
  var ADS_ID="AW-16544169892";
  var LEAD_LABEL="AW-16544169892/V6n9CKDk0LUZEKT_79A9"; // "Enviar formulario de clientes potenciales"
  var GA4_ID=""; // e.g. "G-ABC123XYZ"
  // Optional extra Google Ads conversion labels; fill in when created in Google Ads.
  var LABELS={call:"",whatsapp:"",text:"",booking:""};

  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}
  window.gtag=window.gtag||gtag;
  gtag("js",new Date());
  gtag("config",ADS_ID);
  if(GA4_ID)gtag("config",GA4_ID);

  var lang=(document.documentElement.lang||"en").slice(0,2);
  function ev(name,params){params=params||{};params.page_language=lang;params.page_path=location.pathname;window.gtag("event",name,params);}
  function lead(kind){ev("generate_lead",{lead_type:kind});window.gtag("event","conversion",{send_to:LEAD_LABEL});}
  function contact(kind){ev("contact_click",{method:kind});if(LABELS[kind])window.gtag("event","conversion",{send_to:LABELS[kind]});}

  document.addEventListener("click",function(e){
    var a=e.target.closest&&e.target.closest("a[href]");if(!a)return;
    var h=a.getAttribute("href")||"";
    if(a.id==="sendWa"||a.id==="sendSms"){lead(a.id==="sendWa"?"designer_whatsapp":"designer_text");return;}
    if(h.indexOf("tel:")===0)contact("call");
    else if(h.indexOf("sms:")===0)contact("text");
    else if(h.indexOf("wa.me/")>-1||h.indexOf("api.whatsapp.com")>-1)contact("whatsapp");
    else if(h.indexOf("book.housecallpro.com")>-1)contact("booking");
  },true);

  document.addEventListener("submit",function(e){
    var f=e.target;if(!f||!f.id)return;
    if(f.id==="est")lead("estimate_form");
    else if(f.id==="qform")ev("designer_estimate_created",{});
  },true);

  document.addEventListener("click",function(e){
    var b=e.target.closest&&e.target.closest("#dlPdf,#dlHtml");
    if(b)ev("designer_estimate_download",{format:b.id==="dlPdf"?"pdf":"html"});
  },true);
})();
