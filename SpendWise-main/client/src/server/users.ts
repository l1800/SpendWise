import axios from "axios"
import { p } from "../config"

export const getUser=async()=>{
 return await axios.get(`${p}/Users/getUsers`)
}
export const getUserById=async(id:number)=>{
 return await axios.get(`${p}/Users/getUsersById/${id}`)
}

export const CreateUsers=async(data:object)=>{
 return await axios.post(`${p}/Users/Createuser`,data)
}
export const getUserByPassword=async(data:object)=>{
    try{
        console.log("הצליח")
        const res=await axios.post(`${p}/Users/getUsersByPassword`,data)
        return res;
    }
    catch(e){
        console.log("נכשל")
        console.log(e);
        // alert("משתמש לא קיים")
    }
}