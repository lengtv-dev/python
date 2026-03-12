export default {
 async fetch(request) {

  const url = "https://raw.githubusercontent.com/USER/REPO/main/playlist.json"

  const res = await fetch(url)

  const data = await res.text()

  return new Response(data,{
   headers:{
    "content-type":"application/json",
    "Access-Control-Allow-Origin":"*"
   }
  })

 }
}
