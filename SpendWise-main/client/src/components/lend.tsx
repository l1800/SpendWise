import { useContext } from "react"
//import { Link } from "react-router-dom"
import { UserContext } from "../context/userContext"
//import AddBook from "./addBook"
import { getLendByUserId } from "../server/lend"
//import type { User } from "../models/Users"
import { type Lend } from "../models/Lend"
import { useEffect, useState } from "react"
import { useLocation } from "react-router-dom"

const Lends=()=>
    {
        
        const {pathname}=useLocation()
        console.log(pathname)
        const [lends,setLends]=useState<Lend[]>([])
        const{user}=useContext(UserContext)
        useEffect
        (()=>{
            const myFunc=async()=>
                {
                    const id=user?user.id:-1
                    const res=await getLendByUserId(id)
                    setLends(res.data)
                    console.log(res.data);
                    
                }
        myFunc()
    }, [])
    return(
        <>
        {pathname=='lend'&&<h3>ההשאלות שלי</h3>}
        {
            lends.map(x=><>
            
            <div>שם הספר: {x.book.title}</div>
                {x.lendingDate}
            <hr/>
            </>
            )
        }
        </>
    )      
}
export default Lends
