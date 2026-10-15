import { useState } from "react";
import { useForm } from "react-hook-form"
import { addBook } from "../server/book";
import { useNavigate } from "react-router-dom";
export interface bookValues{
    id:number,
    title:string,
    author:string,
    image:string,
    summary:string,
    pageCount:number,
    categoryName:number
    }
    const AddBook:React.FC=()=>{
        const [book,setBook]=useState();
         const nav=useNavigate();
        const {register,handleSubmit,formState:{errors}}=useForm<bookValues>();
        const onSubmit=async(data:bookValues)=>{
            console.log("הנתונים נשלחו")
            console.log(data)
            const rs=await addBook(data);
            setBook(rs?.data)
            nav(-1)
            console.log(errors);
            
            
        };
    
    return(<>
    <form onSubmit={handleSubmit(onSubmit)}>
    <input
    {...register("title",{required:"הכנס שם ספר"})}
    placeholder="שם הספר"
    />
    {errors.title&&<p>{errors.title.message}</p>}
    
    <input
    {...register("author",{required:"הכנס שם הסופר"})}
    placeholder="הסופר"
    />
    {errors.author&&<p>{errors.author.message}</p>}
    
    <input
    {...register("image",{required:"הכנס את ניתוב התמונה"})}
    placeholder="תמונה"
    />
    {errors.image&&<p>{errors.image.message}</p>}
    
    <input
    {...register("summary",{required:"הכנס את התקציר"})}
    placeholder="התקציר"
    />
    {errors.summary&&<p>{errors.summary.message}</p>}
    
    <input
    type="number"
    {...register("pageCount",{required:"הכנס מספר עמודים"})}
    placeholder="מספר עמודים"
    />
    {errors.pageCount&&<p>{errors.pageCount.message}</p>}
    
    <input
    type="number"
    {...register("categoryName",{required:"הכנס קטגוריה"})}
    placeholder="הכנס קטגוריה בין 1-3"
    />
    {errors.categoryName&&<p>{errors.categoryName.message}</p>}
    <button type="submit">שלח</button>
    </form>
    </>)
    }
    export default AddBook
    