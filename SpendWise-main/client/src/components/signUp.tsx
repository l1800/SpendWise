import { useForm } from "react-hook-form"
import { CreateUsers} from "../server/users"
import { useContext } from "react"
import { UserContext } from "../context/userContext"
import { useNavigate } from "react-router-dom"
import * as yup from "yup";
import { yupResolver } from "@hookform/resolvers/yup"
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

export const schema = yup.object({ 
    firstName: yup.string().matches(/[a-z]+/, 'Is not in correct format').required(),
    lastName: yup.string().matches(/[a-z]+/, 'Is not in correct format').required(),
    userName: yup.string().required(),
    password:yup.string().max(4).required(),
    tz:yup.string().required(),
    phoneNumber:yup.string().max(10).matches(/[0-9]+/, 'Is not in correct format').required(),
    mail:yup.string().email().required(),
}).required();

// import { useForm } from "react-hook-form"
// import { CreateUsers } from "../server/users"
// export interface FormValues{
//     id: 0,
//   userName: string,
//   password: string,
//   tz: string,
//   firstName: string,
//   lastName: string,
//   phoneNumber:string,
//   mail: string,
//   status: boolean
//     }
const signUp:React.FC=()=>{
    const{setUser,user}=useContext(UserContext)
    const nav=useNavigate();

     const {register,handleSubmit,formState:{errors}}=useForm({
      resolver: yupResolver(schema),
      });

    const onSubmit=async(data:Object)=>{
        console.log("הנתונים נשלחו")
        console.log(data);
        const res=await CreateUsers(data);
        setUser(res?.data);        
        {res&&nav("/Home")}
    };
    // const {register,handleSubmit,formState:{errors}}=useForm<FormValues>();
    // const onSubmit=(data:FormValues)=>{
    //     console.log("הנתונים נשלחו")
    //     console.log(data)
    //     CreateUsers(data)
    // };
return(<>
<form onSubmit={handleSubmit(onSubmit)}>

<input
{...register("userName",{required:"יש להזין שם משתמש"})}
placeholder="שם משתמש"
/>
{errors.userName&&<p>{errors.userName.message}</p>}

<input
type="password"
{...register("password",{required:"יש להזין סיסמא"})}
placeholder="סיסמא"
/>
{errors.password&&<p>{errors.password.message}</p>}

<input
{...register("tz",{required:"יש להזין תעודת זהות"})}
placeholder="תעודת זהות"
/>
{errors.tz&&<p>{errors.tz.message}</p>}

<input
{...register("firstName",{required:"יש להזין שם פרטי"})}
placeholder="שם פרטי"
/>
{errors.firstName&&<p>{errors.firstName.message}</p>}

<input
{...register("lastName",{required:"יש להזין שם משפחה"})}
placeholder="שם משפחה"
/>
{errors.lastName&&<p>{errors.lastName.message}</p>}

<input
type="number"
{...register("phoneNumber",{required:"יש להזין טלפון"})}
placeholder="טלפון"
/>
{errors.phoneNumber&&<p>{errors.phoneNumber.message}</p>}

<input
type="email"
{...register("mail",{required:"יש להזין כתובת מייל"})}
placeholder="מייל"
/>
{errors.mail&&<p>{errors.mail.message}</p>}

<button type="submit">שלח</button>

</form>
</>)
}
export default signUp
