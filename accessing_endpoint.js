async function getting_tasks_from_backend(){
    try
    {
        let response=await fetch('http://127.0.0.1:5000/post_tasks')
        let data= await response.json()
        console.log(data)
    }
    catch(err){
        console.error(err)
    }
}

getting_tasks_from_backend()
