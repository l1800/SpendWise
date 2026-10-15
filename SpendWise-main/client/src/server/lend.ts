import axios from "axios"
import {p}from "../config"
export const addLend = async (data:object) => {
    const res = await axios.post(`${p}/Lend/CreateLend`,data)    
    return res
}
export const getLendByUserId=async(id:number)=>{
    return await axios.get(`${p}/Lend/getLendByUserId/${id}`)
}