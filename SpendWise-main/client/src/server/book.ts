import axios from "axios"
import { p } from "../config"

export const getBooks = async () => {
    try{
        const res=await axios.get(`${p}/book/getBooks`)
        return res
    }
    catch(e){
        
    }
    
}
export const getCommentById = async (id:number) => {
    const res = await axios.get(`${p}/Comment/getCommentById/${id}`)    
    return res
}
export const getLendById = async (id:number) => {
    const res = await axios.get(`${p}/Lend/getLendById/${id}`)    
    return res
}
export const addBook=async(data:object)=>{
    try{
    return await axios.post(`${p}/book/CreateBook`,data) }
    catch(e){
        console.log(e);
    }
}

export const deletebook=async(id:number)=>{
    await axios.delete(`/book/deleteBook/${id}`)  
}
export const getBookById=async(id:number)=>{
    await axios.get(`${p}/book/getBookById/${id}`)
}
