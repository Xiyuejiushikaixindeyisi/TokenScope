// Joint acceptance only: streaming gzip on real backend exports; no production configuration.
import http from 'node:http';
import { createGzip } from 'node:zlib';
const server=http.createServer((req,res)=>{
 const upstream=http.request({hostname:'127.0.0.1',port:8186,path:req.url,method:req.method,headers:{...req.headers,host:'127.0.0.1:8186'}},r=>{
  const headers={...r.headers};delete headers['content-length'];delete headers['transfer-encoding'];
  if(req.url.includes('/requests/export?') && r.statusCode===200){
   headers['content-encoding']='gzip';res.writeHead(r.statusCode,headers);const gzip=createGzip({chunkSize:65536});r.pipe(gzip).pipe(res);res.on('close',()=>{r.destroy();gzip.destroy();});gzip.on('error',()=>res.destroy());
  }else{res.writeHead(r.statusCode,headers);r.pipe(res);res.on('close',()=>r.destroy());}
 });upstream.on('error',()=>{if(!res.headersSent)res.writeHead(502);res.end();});req.pipe(upstream);res.on('close',()=>upstream.destroy());
});server.listen(8188,'127.0.0.1',()=>console.log('Joint gzip proxy 8188 -> 8186'));
