// import {p } from "../config"
// import axios from "axios"
import { useEffect, useState } from "react"
import {type Book } from "../models/Book"
import { getBooks, getCommentById, getLendById } from "../server/book"
// import  AddComment  from "./addComment"
// import { Link } from "react-router-dom"
// import { deletebook } from "../server/book"
import { type Comment } from "../models/Comment"
// import { getBookById } from "../server/book"
import { UserContext } from "../context/userContext";
import  { useContext } from "react"
import { addLend } from "../server/lend"
import type { Lend } from "../models/Lend"
import OneBook from "./OneBook"
import Stack from "@mui/material/Stack"
import { useLocation } from "react-router-dom"

const Show=()=>{
    const{user,setUser}=useContext(UserContext)
    const[books,setBooks]=useState<Book[]>([])
    const [commants,setComment]=useState<Comment[]>([])
    const [lend,setLend]=useState<Lend[]>([])
 const {pathname}=useLocation()
 console.log(pathname)
    const myFunc = async () => {
            const res =await getBooks()
            console.log(res?.data);
            setBooks(res?.data)      
        }
    useEffect(()=>{
        myFunc()
    }, [])
    const getComment=async(id:number)=>{
        const x=await getCommentById(id)
        setComment(x.data)
    }
    // const addComment=async()=>{
    //  <Link to={"/addComment"}>addComment</Link> 
    // }
    // const deleteBook=(id:number)=>{
    //     deletebook(id)
    //     const res=books.filter(x=>x.id!=id)
    //     setBooks(res)
    // }
    const toLend=async(book:Book)=>{
        const data={book:book,user:user,lendingDate:new Date()}
        console.log("הנתונים נשלחו")
        console.log(data)
        const res=await addLend(data);
        setLend(res?.data)
        
    }
    return  <>
   <div> <h1>רשימת כל הספרים</h1></div>
   <Stack direction={'row'} flexWrap={'wrap'} gap={2}>
   {books.map(x =><>
   <OneBook book={x}/>
   </>)}
   {/* {Comment.map(y=>  <>
   <p >{`Author's note :${y.content}`}</p>
   </>)} */}
   </Stack>
    </>
    }
    export default Show


