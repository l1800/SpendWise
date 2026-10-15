import { UserContext } from "../context/userContext";
import React, { useContext } from "react"
import { useForm } from "react-hook-form"
import { useNavigate } from "react-router-dom";
import { getUserByPassword } from "../server/users";
import type { User } from "../models/Users";

const Login:React.FC=()=>{
    const{user,setUser}=useContext(UserContext)
    const nav=useNavigate();
    const {register,handleSubmit,formState:{errors}}=useForm<User>();

    const onSubmit=async(data:User)=>{
        console.log("הנתונים נשמרו");
        const res=await getUserByPassword(data)
        console.log(res)
        setUser(res?.data)
        {if(res?.data.userName!=null)
            nav("/signUp")
        else{
            nav(-1)
        }}   
    }
return(
    <div>
    <form onSubmit={handleSubmit(onSubmit)}>
    <input {...register("userName",{required:"הכנס שם משתמש"})}
    placeholder="שם משתמש"
      />
      {errors.userName&&<p>{errors.userName.message}</p>}
      <input {...register("password",{required:"הכנס סיסמא"})}
      placeholder="סיסמא"
      />
      {errors.password&&<p>{errors.password?.message}</p>}
      <button type="submit">שלח</button>
    </form>
    
    </div>
  )
}

export default  Login