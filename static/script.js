const input=document.getElementById("textInput"),counter=document.getElementById("counter"),result=document.getElementById("result"),error=document.getElementById("error");
let latestResult=null;
const historyKey="biasHistory";

input.addEventListener("input",()=>counter.textContent=`${input.value.length} / 1000`);
document.getElementById("clearBtn").onclick=()=>resetAnalyzer();
document.getElementById("newChat").onclick=()=>{resetAnalyzer();input.focus();window.scrollTo({top:0,behavior:"smooth"});};
document.getElementById("historyBtn").onclick=()=>document.getElementById("historyCard").scrollIntoView({behavior:"smooth",block:"start"});
document.getElementById("performanceBtn").onclick=()=>window.location.href="/performance";

function resetAnalyzer(){input.value="";counter.textContent="0 / 1000";error.textContent="";result.classList.add("hidden");latestResult=null;}

document.getElementById("exampleBtn").onclick=()=>{const items=[...document.querySelectorAll(".bias-item")];if(items.length){const item=items[Math.floor(Math.random()*items.length)];loadText(item.dataset.example);}};
function loadText(text){input.value=text;input.dispatchEvent(new Event("input"));window.scrollTo({top:0,behavior:"smooth"});input.focus();}

document.querySelectorAll(".bias-item").forEach(b=>b.onclick=()=>loadText(b.dataset.example));

document.getElementById("biasSearch").addEventListener("input",e=>{const q=e.target.value.toLowerCase().trim();document.querySelectorAll(".bias-item").forEach(b=>b.classList.toggle("hidden-card",q&&!b.dataset.name.includes(q)&&!b.textContent.toLowerCase().includes(q)));});

function showResult(data){
 document.getElementById("biasName").textContent=data.bias_name;document.getElementById("confidence").textContent=data.confidence+"%";
 const level=data.confidence>=80?"High Confidence":data.confidence>=60?"Moderate Confidence":"Low Confidence";const badge=document.getElementById("confidenceLevel");badge.textContent=level;badge.dataset.level=level.split(" ")[0].toLowerCase();
 document.getElementById("description").textContent=data.description;document.getElementById("whyDetected").textContent=data.why_detected;document.getElementById("tip").textContent=data.tip;
 const multi=document.getElementById("multiBias"),possible=document.getElementById("possibleBiases");possible.innerHTML="";
 if(data.possible_biases&&data.possible_biases.length){multi.classList.remove("hidden");data.possible_biases.forEach(x=>{possible.innerHTML+=`<span class="possible-pill">${escapeHtml(x.name)} — ${x.score}%</span>`;});}else multi.classList.add("hidden");
 const scores=document.getElementById("scores");scores.innerHTML="";Object.entries(data.scores).sort((a,b)=>b[1]-a[1]).forEach(([key,val])=>{const name=key.replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());scores.innerHTML+=`<div class="score"><div class="score-top"><span>${name}</span><span>${val}%</span></div><div class="bar"><div class="fill" style="width:${Math.min(val,100)}%"></div></div></div>`;});result.classList.remove("hidden");result.classList.remove("pop-in");void result.offsetWidth;result.classList.add("pop-in");}

document.getElementById("analyzeBtn").onclick=async()=>{error.textContent="";const text=input.value.trim();if(!text){error.textContent="Please enter some text first.";return;}const btn=document.getElementById("analyzeBtn");btn.disabled=true;btn.textContent="Analyzing...";try{const res=await fetch("/predict",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text})});const data=await res.json();if(!res.ok)throw new Error(data.error||"Analysis failed");latestResult={text,...data};showResult(data);saveHistory(text,data);renderHistory();renderStats();result.scrollIntoView({behavior:"smooth"});}catch(e){error.textContent=e.message}finally{btn.disabled=false;btn.textContent="Analyze";}};

function saveHistory(text,data){const h=JSON.parse(localStorage.getItem(historyKey)||"[]");h.unshift({text,bias:data.bias_name,confidence:data.confidence,time:new Date().toLocaleString()});localStorage.setItem(historyKey,JSON.stringify(h.slice(0,100)));}
function getHistory(){return JSON.parse(localStorage.getItem(historyKey)||"[]");}
function renderHistory(){const h=getHistory();const el=document.getElementById("history");if(!h.length){el.innerHTML='<p class="empty">No analyses yet.</p>';return;}el.innerHTML=h.map((x,i)=>`<div class="history-item" data-i="${i}"><strong>${escapeHtml(x.bias)} — ${x.confidence}%</strong><span>${escapeHtml(x.time)}</span><p>${escapeHtml(x.text)}</p><small>Click to reuse this text</small></div>`).join("");document.querySelectorAll(".history-item").forEach(el=>el.onclick=()=>{const x=h[Number(el.dataset.i)];loadText(x.text);});}
function renderStats(){const h=getHistory();document.getElementById("totalAnalyses").textContent=h.length;document.getElementById("donutTotal").textContent=h.length;if(!h.length){document.getElementById("mostBias").textContent="—";document.getElementById("avgConfidence").textContent="0%";document.getElementById("statsBars").innerHTML='<p class="empty">Analyze some text to build statistics.</p>';document.getElementById("donutChart").style.background="conic-gradient(#e5e7eb 0 100%)";return;}const counts={};let total=0;h.forEach(x=>{counts[x.bias]=(counts[x.bias]||0)+1;total+=Number(x.confidence)||0;});const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]);document.getElementById("mostBias").textContent=sorted[0][0];document.getElementById("avgConfidence").textContent=(total/h.length).toFixed(1)+"%";const max=sorted[0][1];document.getElementById("statsBars").innerHTML=sorted.map(([name,count])=>`<div class="stat-row"><div class="score-top"><span>${escapeHtml(name)}</span><span>${count}</span></div><div class="bar"><div class="fill" style="width:${(count/max)*100}%"></div></div></div>`).join("");let cursor=0;const parts=sorted.map(([name,count],i)=>{const pct=count/h.length*100;const start=cursor;cursor+=pct;return `${chartColor(i)} ${start}% ${cursor}%`;});document.getElementById("donutChart").style.background=`conic-gradient(${parts.join(",")})`;}
function chartColor(i){const colors=["#2563eb","#7c3aed","#059669","#ea580c","#db2777","#0891b2","#65a30d","#ca8a04"];return colors[i%colors.length];}

// Sample library
const sampleTabs=document.querySelectorAll(".sample-tab"),sampleList=document.getElementById("sampleList");function renderSamples(category){sampleList.innerHTML=(window.SAMPLE_LIBRARY[category]||[]).map(t=>`<button class="sample-item" data-text="${escapeAttr(t)}">${escapeHtml(t)}<span>Analyze this →</span></button>`).join("");sampleList.querySelectorAll(".sample-item").forEach(b=>b.onclick=()=>loadText(b.dataset.text));}sampleTabs.forEach((b,i)=>b.onclick=()=>{sampleTabs.forEach(x=>x.classList.remove("active"));b.classList.add("active");renderSamples(b.dataset.category);});if(sampleTabs.length){sampleTabs[0].classList.add("active");renderSamples(sampleTabs[0].dataset.category);}

// History export
 document.getElementById("downloadHistory").onclick=async()=>{const h=getHistory();if(!h.length){error.textContent="There is no history to export yet.";return;}const res=await fetch("/download-history-csv",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({history:h})});const blob=await res.blob();const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="cognitive_bias_history.csv";a.click();URL.revokeObjectURL(url);};

document.getElementById("clearHistory").onclick=()=>{localStorage.removeItem(historyKey);renderHistory();renderStats();};
document.getElementById("copyBtn").onclick=async()=>{if(!latestResult)return;const text=`Input: ${latestResult.text}\nBias: ${latestResult.bias_name}\nConfidence: ${latestResult.confidence}%\nWhy: ${latestResult.why_detected}\nExplanation: ${latestResult.description}\nTip: ${latestResult.tip}`;await navigator.clipboard.writeText(text);const b=document.getElementById("copyBtn");const old=b.textContent;b.textContent="✓ Copied";setTimeout(()=>b.textContent=old,1200);};
document.getElementById("pdfBtn").onclick=async()=>{if(!latestResult)return;const res=await fetch("/download-report",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(latestResult)});if(!res.ok){error.textContent="Could not create PDF report.";return;}const blob=await res.blob();const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download="cognitive_bias_report.pdf";a.click();URL.revokeObjectURL(url);};

// Theme
const savedTheme=localStorage.getItem("biasTheme")||"light";if(savedTheme==="dark")document.body.classList.add("dark");function updateThemeButton(){document.getElementById("themeToggle").textContent=document.body.classList.contains("dark")?"☀️ Light":"🌙 Dark";}document.getElementById("themeToggle").onclick=()=>{document.body.classList.toggle("dark");localStorage.setItem("biasTheme",document.body.classList.contains("dark")?"dark":"light");updateThemeButton();};updateThemeButton();
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));}function escapeAttr(s){return String(s).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
renderHistory();renderStats();
