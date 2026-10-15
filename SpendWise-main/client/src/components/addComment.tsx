// import { useForm } from "react-hook-form"
// import { addCommentById } from "../server/comment"
// export interface commentValues{
//   content: string,
//   date: Date,
//   book: number
//     }
// const AddComment:React.FC=()=>{
//     const {register,handleSubmit,formState:{errors}}=useForm<commentValues>();
//     const onSubmit=(data:commentValues)=>{
//         console.log("הנתונים נשלחו")
//         console.log(data)
//         addComment1(data)
//     };

// return(<>
// <form onSubmit={handleSubmit(onSubmit)}>

// <input
// type="number"
// {...register("book",{required:"enter book id"})}
// placeholder="bookId"
// />
// {errors.book&&<p>{errors.book.message}</p>}
// <input
// type="date"
// {...register("date",{required:"enter date"})}
// placeholder="comment date"
// />
// <input
// {...register("content",{required:"enter your comment"})}
// placeholder="the comment"
// />
// <button type="submit">שלח</button>

// </form>
// </>)
// }
// export default AddComment
