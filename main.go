package main

import (
	"github.com/kataras/iris/v12"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	"log"
)

func main() {
	session, err := mgo.Dial("mongodb://coc:SakuraYui@localhost:27017/coc")
	if err != nil {
		log.Fatal(err)
	}
	log.Print("successfully connect to db")
	playerData := session.DB("coc").C("playerData")
	server := iris.Default()
	crs := func(ctx iris.Context) {
		ctx.Header("Access-Control-Allow-Origin", "https://www.diving-fish.com")
		ctx.Header("Access-Control-Allow-Credentials", "true")
		ctx.Header("Access-Control-Allow-Headers", "Access-Control-Allow-Origin,Content-Type,Authorization")
		if ctx.Method() == "OPTIONS" {
			return
		}
		ctx.Next()
	}
	server.Use(crs)
	server.Post("/insert", func(ctx iris.Context) {
		data := bson.M{}
		_ = ctx.ReadJSON(&data)
		_ = playerData.Insert(data)
	})
	server.Get("/query", func(ctx iris.Context) {
		name := ctx.URLParam("name")
		data := bson.M{}
		_ = playerData.Find(bson.M{"name": name}).One(&data)
		ctx.JSON(data)
	})
	server.Run(iris.Addr(":25565"))
}