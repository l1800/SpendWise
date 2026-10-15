import { p} from "../config"
import axios from "axios"
export const getCommentById = async (id:number) => {
    const res = await axios.get(`${p}/Comment/getCommentById/${id}`)    
    return res
}
export const addCommentById=async (bookId:number)=>{
    const res=await axios.get(`${p}/comment/getCommentsByBookId/${bookId}`)
    return res
 }