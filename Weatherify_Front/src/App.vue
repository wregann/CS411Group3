<template>
  <div :style="image" class="image"></div>

  <div id="app">
    <h1>Weatherify</h1>
    <p>music meets weather</p>
    <p>Logged: {{logged}}</p>
    <p>Url: {{auth_url}}</p>
  </div>
  <!-- <div id="nav">
    <router-link to="/">Home</router-link>
    <router-link to="/Login">Login</router-link>
  </div>
  <router-view/> -->
  <button v-if="!logged" v-on:click="window.location.href=auth_url">Login</button>
  <div id="creator" v-if="logged">

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

      </tbody>
    </table>
  </div>
 

</template>

<script>
import axios from 'axios';
export default {
  el: '#app',
    data() {
      return {
        image: {backgroundImage: "url(https://i.pinimg.com/originals/dd/14/ee/dd14ee38df85f17a1054668f74546c30.jpg)"},
        days: [],
        logged: false,
        auth_url: null
      }
    },
    mounted() {
      try{
        axios.get('http://127.0.0.1:1000/get_5_days').then(response => {this.days = response.data.days}),
        axios.get('http://127.0.0.1:1000/').then(response => {this.logged = response.data.logged; this.auth_url = response.data.auth_url})
      }
      catch(err){
        console.log(err)
      }
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
    font-size: 30px;
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
