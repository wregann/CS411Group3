<template>

  <div id="app">
    <div class="header">
      <h1 style="font-size: xxx-large">Weatherify</h1>
      <p style="font-size: large">music meets weather</p>
    </div>

    <!-- Display Information -->
    <p>Logged In: {{logged}}</p>
    <p v-if="!logged">Spotify Login Url: {{auth_url}}</p>
    <p v-if="logged">ID: {{user_id}} <br></p>

    <!-- Log in and out Buttons -->
    <button v-if="!logged" @click=spotifyLogin()>Login</button>
    <button v-if="logged" @click=logout()>Log Out</button>

    <!-- City Input -->
    <div v-if="logged" id="City_Input">
      <form v-on:submit.prevent="submit_city">
        <input type="text" placeholder="Input Closest City Here" v-model="city_string"/>
        <button @click="submit_city()">Submit City</button>
      </form>
      <p>City Found: {{city_found}}</p>
      <p>Latitude: {{lat}}, Longitude: {{long}}</p>
    </div>

    <!-- Main Creator Portion -->
    <div id="creator" v-if="logged && city_found">
      <form v-on:submit.prevent="submit_weather">
        <table border="1" class="center">
          <thead>
            <tr>
                <th>{{days[0]}}</th>
                <th>{{days[1]}}</th>
                <th>{{days[2]}}</th>
                <th>{{days[3]}}</th>
                <th>{{days[4]}}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td> {{day_mains[0]}} <br> {{day_descs[0]}} <br> {{day_temps[0]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="0" /></td>
              <td> {{day_mains[1]}} <br> {{day_descs[1]}} <br> {{day_temps[1]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="1"/></td>
              <td> {{day_mains[2]}} <br> {{day_descs[2]}} <br> {{day_temps[2]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="2"/></td>
              <td> {{day_mains[3]}} <br> {{day_descs[3]}} <br> {{day_temps[3]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="3"/></td>
              <td> {{day_mains[4]}} <br> {{day_descs[4]}} <br> {{day_temps[4]}} <br> <input type="radio" name="DaySelect" v-model="selected_day" :value="4"/></td>
            </tr>
          <!-- Evening Temps... Maybe Later
          <tr>
            <td>{{eve_mains[0]}} <br> {{eve_descs[0]}} <br> {{eve_temps[0]}} </td>
            <td>{{eve_mains[1]}} <br> {{eve_descs[1]}} <br> {{eve_temps[1]}} </td>
            <td>{{eve_mains[2]}} <br> {{eve_descs[2]}} <br> {{eve_temps[2]}} </td>
            <td>{{eve_mains[3]}} <br> {{eve_descs[3]}} <br> {{eve_temps[3]}} </td>
            <td>{{eve_mains[4]}} <br> {{eve_descs[4]}} <br> {{eve_temps[4]}} </td>
          </tr>
          -->
          </tbody>
        </table>
        <button>Submit Weather To Make Playlist!</button>
      </form>
    </div>
    <p v-if="city_found">Created: {{playlist_created}}</p>
    <p v-if="city_found">Playlist Name: {{playlist_name}}</p>
    <p v-if="city_found">Created At: {{created_when}}</p>
  </div>
</template>

<script>
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';
import {computed, watch} from 'vue'


export default {
  el: '#app',
    data() {
      return {
        image: {backgroundImage: "url(https://i.pinimg.com/originals/dd/14/ee/dd14ee38df85f17a1054668f74546c30.jpg)"},
        days: [],
        logged: false,
        auth_url: null,
        user_id: null,
        city_string: null,
        city_found: false,
        lat: 0,
        long: 0,
        day_mains: ["", "", "", "", ""],
        day_descs: ["", "", "", "", ""],
        day_temps: [0,0,0,0,0],
        eve_mains: ["", "", "", "", ""],
        eve_descs: ["", "", "", "", ""],
        eve_temps: [0,0,0,0,0],
        selected_day: null,
        playlist_created: false,
        playlist_name: "",
        created_when: null
      }
    },
    mounted() {
      axios.defaults.withCredentials=true     
      try{
        axios.get('http://127.0.0.1:1000/api/get_5_days').then(response => {console.log(response); this.days = response.data.days})
        axios.get('http://127.0.0.1:1000/api/').then(response => {this.logged = response.data.logged; this.user_id = response.data.user_id; this.auth_url = response.data.auth_url})       
      }
      catch(err){
        console.log(err)
      }
    },
    methods : {
      spotifyLogin(){
        window.location.href = this.auth_url;
      },
      logout(){
        try{
          axios.get('http://127.0.0.1:1000/api/out').then(response => {console.log(response); this.logged = false; this.auth_url = null; this.user_id = null})
          this.$router.push('/')
          axios.get('http://127.0.0.1:1000/api/').then(response => {this.logged = response.data.logged; this.user_id = response.data.user_id; this.auth_url = response.data.auth_url})       

        }
        catch(err){
          console.log(err)
        }
      },
      submit_city() {
        this.$emit('submit', this.city_string)
        try{
          //console.log('http://127.0.0.1:1000/api/get_weather_data/' + this.city_string)
          axios.get('http://127.0.0.1:1000/api/get_weather_data/' + this.city_string).then(response => {console.log(response); this.lat = response.data.lat; this.long = response.data.lon; this.city_found = (this.lat) ? true : false;
          if (this.city_found) {
            for (let i = 0; i < 5; i++) {
              this.day_mains[i] = response.data.daily[i].weather[0].main
              this.day_descs[i] = response.data.daily[i].weather[0].description
              this.day_temps[i] = response.data.daily[i].feels_like.day
            }
          }
          })
        }
        catch(err){
          console.log(err)
        }
      },
      submit_weather() {
        console.log(this.selected_day)
        try {
          if (this.selected_day >= 0 && this.selected_day <= 4){
            axios.post('http://127.0.0.1:1000/api/go', {withCredentials : true,
                      main: this.day_mains[this.selected_day],
                      description: this.day_descs[this.selected_day],
                      temperature: this.day_temps[this.selected_day]
                    }).then(response => {this.playlist_created = response.data.Created; this.playlist_name = response.data.Name; this.created_when = response.data.when})
          }
          
        }
        catch(err) {
          console.log(err)
        }
      }
    },
    setup() {
      // const router = useRouter()
      // router.isReady()
      // const route = useRoute()
      
      // const searchQuery = computed(() => route.query.code)

      // let user_code = null
      
      // watch(searchQuery, newSearchQuery => {console.log(newSearchQuery); user_code = newSearchQuery})
  
      // return {
      //   user_code
      // }
      
      
    }
}
</script>

<style>
#app {
  text-align: center;
  color: #2c3e50;
  margin-top: 40px;
}
.image {
      height: 500px;
      margin-left: 200px;
      margin-right: 200px;
      background-repeat: no-repeat;
  }
.header {
    padding: 5px;
    text-align: center;
    background: #0baff0;
    color: whitesmoke;
}
table {
    margin-top: 1%;
    box-shadow: 0 0 20px 0 rgba(0, 0, 0, 0.2), 0 5px 5px 0 rgba(0, 0, 0, 0.24);
}
table th {
    padding-left: 30px;
    padding-right: 30px;
    padding-top: 10px;
    padding-bottom: 10px;
    text-align: center;
    color: #000000;
}
table td{
    align-items: center;
    white-space: nowrap;
    text-align: center;
    color: #000000;
}
.center {
    text-align: center;
    margin-left: auto;
    margin-right: auto;
}
</style>
